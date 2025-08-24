#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
依據 frontend/student-app/files/三版本科目章節.json 的標準章節，
掃描 database/seeds/全題庫/ 下所有題目 JSON 的 chapter 欄位，
自動建立 raw chapter -> 標準章節 的對應表，輸出到：
frontend/student-app/files/chapter_mapping.json

執行環境：Linux/WSL，標準 Python 3（無需額外套件）。
用法：
  cd 2_implementation/scripts
  python3 gen_chapter_mapping.py
"""

import json
import sys
import re
from pathlib import Path
from difflib import SequenceMatcher

ROOT = Path(__file__).resolve().parents[1]
CANONICAL_PATH = ROOT / 'frontend' / 'student-app' / 'files' / '三版本科目章節.json'
SEEDS_DIR = ROOT / 'database' / 'seeds' / '全題庫'
OUTPUT_PATH = ROOT / 'frontend' / 'student-app' / 'files' / 'chapter_mapping.json'

PUBLISHERS = ['南一', '翰林', '康軒']
SUBJECTS = ['國文', '英文', '數學', '自然', '地理', '歷史', '公民']


def read_json(path: Path):
    with path.open('r', encoding='utf-8') as f:
        return json.load(f)


def normalize(text: str) -> str:
    if not text:
        return ''
    t = str(text)
    # 全形轉半形（僅常見標點/空白）
    t = t.replace('．', '.').replace('　', ' ')
    # 去空白
    t = re.sub(r"\s+", '', t)
    # 去常見標點
    t = re.sub(r"[，,。.!？?；;：:/\\()\[\]{}<>【】『』“”\"'\-]", '', t)
    return t


def num_prefix(text: str) -> str:
    m = re.match(r'^(\d+(?:[.．-]\d+)?)', str(text))
    return m.group(1) if m else ''


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def collect_canonical() -> dict:
    data = read_json(CANONICAL_PATH)
    canon = {}
    for item in data:
        pub = item.get('出版社')
        subj = item.get('科目')
        grades = item.get('年級章節') or {}
        if pub not in PUBLISHERS or subj not in SUBJECTS:
            continue
        canon.setdefault(pub, {}).setdefault(subj, set())
        for chapters in grades.values():
            for ch in chapters:
                canon[pub][subj].add(ch)
    # 轉成 list
    for pub in canon:
        for subj in canon[pub]:
            canon[pub][subj] = sorted(canon[pub][subj])
    return canon


def detect_pub_from_name(name: str) -> str:
    for p in PUBLISHERS:
        if p in name:
            return p
    return ''


def detect_subj_from_path(path: Path) -> str:
    # /全題庫/科目/檔名.json
    try:
        return path.parent.name
    except Exception:
        return ''


def collect_raw_chapters() -> dict:
    raw = {}
    for file in SEEDS_DIR.rglob('*.json'):
        try:
            subj = detect_subj_from_path(file)
            pub = detect_pub_from_name(file.name)
            if subj not in SUBJECTS or pub not in PUBLISHERS:
                continue
            data = read_json(file)
            # 支援兩種結構：list[question] 或 object{questions:[]}
            if isinstance(data, dict) and 'questions' in data:
                items = data.get('questions') or []
            elif isinstance(data, list):
                items = data
            else:
                items = []
            for q in items:
                ch = q.get('chapter') or q.get('章節') or ''
                if not ch:
                    continue
                raw.setdefault(pub, {}).setdefault(subj, set()).add(str(ch))
        except Exception:
            # 忽略單一檔案錯誤，繼續處理
            continue
    # 轉成 list
    for pub in raw:
        for subj in raw[pub]:
            raw[pub][subj] = sorted(raw[pub][subj])
    return raw


def best_match(raw_text: str, candidates: list) -> str:
    if not candidates:
        return ''
    raw_norm = normalize(raw_text)
    raw_num = num_prefix(raw_text)

    best = ('', 0.0)
    for cand in candidates:
        cand_norm = normalize(cand)
        score = similarity(raw_norm, cand_norm)
        # 提升：數字章節一致加權
        cand_num = num_prefix(cand)
        if raw_num and cand_num and raw_num == cand_num:
            score += 0.2
        # 提升：候選包含/被包含
        if raw_norm and cand_norm and (raw_norm in cand_norm or cand_norm in raw_norm):
            score += 0.1
        if score > best[1]:
            best = (cand, score)
    # 過濾門檻
    return best[0] if best[1] >= 0.55 else ''


def build_mapping():
    canonical = collect_canonical()
    raw = collect_raw_chapters()

    mapping = {}
    for pub in raw:
        for subj in raw[pub]:
            mapping.setdefault(pub, {}).setdefault(subj, {
                'raw_to_canonical': {},
                'canonical_to_raws': {}
            })
            candidates = canonical.get(pub, {}).get(subj, [])
            for r in raw[pub][subj]:
                matched = best_match(r, candidates)
                if matched:
                    mapping[pub][subj]['raw_to_canonical'][r] = matched
                    mapping[pub][subj]['canonical_to_raws'].setdefault(matched, []).append(r)

    # 輸出
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open('w', encoding='utf-8') as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)

    print(f'✅ 章節對應表已輸出：{OUTPUT_PATH}')


if __name__ == '__main__':
    try:
        build_mapping()
    except Exception as e:
        print('❌ 產生章節對應表失敗：', e)
        sys.exit(1)

