console.log('StudentsAnalysisManager loading...');

class StudentsAnalysisManager {
    constructor() {
        console.log('StudentsAnalysisManager constructor called');
        this.currentClassId = null;
        this.currentPage = 1;
        this.pageSize = 20;
        this.totalPages = 0;
        this.totalCount = 0;
        this.students = [];
        this.filteredStudents = [];
        this.charts = {};
        this.sortOrder = 'asc';
        this.sortBy = 'name';
        this.searchTerm = '';
        this.currentView = 'overview';
        this.isInitialized = false;
        this.init();
    }

    async init() {
        if (this.isInitialized) {
            console.log('StudentsAnalysisManager already initialized');
            return;
        }
        
        try {
            console.log('Initializing StudentsAnalysisManager...');
            this.setupEventListeners();
            await this.loadClasses();
            this.checkAuth();
            this.isInitialized = true;
            console.log('StudentsAnalysisManager initialization complete');
        } catch (error) {
            console.error('Initialization failed:', error);
            this.showError('Initialization failed, please check network connection');
        }
    }

    setupEventListeners() {
        console.log('Setting up event listeners...');
        
        // Class selector change event
        const classSelector = document.getElementById('classSelector');
        if (classSelector) {
            classSelector.addEventListener('change', (e) => {
                console.log('Class selected:', e.target.value);
                this.currentClassId = e.target.value;
                this.currentPage = 1;
                if (this.currentClassId) {
                    this.loadClassOverview(this.currentClassId);
                    this.loadStudents(this.currentClassId);
                } else {
                    this.showNoDataState();
                }
            });
        }

        // Refresh button
        const refreshBtn = document.getElementById('refreshBtn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                console.log('Refresh button clicked');
                if (this.currentClassId) {
                    this.loadClassOverview(this.currentClassId);
                    this.loadStudents(this.currentClassId);
                }
            });
        }

        // View toggle buttons
        this.setupViewToggle();
    }

    setupViewToggle() {
        console.log('Setting up view toggle...');
        
        // Create view toggle buttons
        const viewToggleContainer = document.createElement('div');
        viewToggleContainer.className = 'mb-6 flex justify-center space-x-4';
        viewToggleContainer.innerHTML = `
            <button id="overviewViewBtn" class="px-4 py-2 rounded-lg bg-blue-600 text-white font-medium hover:bg-blue-700 transition-colors">
                <span class="material-icons mr-2">analytics</span>Class Overview
            </button>
            <button id="listViewBtn" class="px-4 py-2 rounded-lg bg-gray-200 text-gray-700 font-medium hover:bg-gray-300 transition-colors">
                <span class="material-icons mr-2">people</span>Student List
            </button>
        `;

        // Insert after class selector
        const classSelector = document.getElementById('classSelector');
        if (classSelector && classSelector.parentElement) {
            classSelector.parentElement.parentElement.after(viewToggleContainer);
        }

        // Bind view toggle events
        document.getElementById('overviewViewBtn').addEventListener('click', () => this.switchView('overview'));
        document.getElementById('listViewBtn').addEventListener('click', () => this.switchView('list'));
    }

    switchView(view) {
        console.log('Switching to view:', view);
        this.currentView = view;
        
        // Update button states
        document.getElementById('overviewViewBtn').className = 
            view === 'overview' 
                ? 'px-4 py-2 rounded-lg bg-blue-600 text-white font-medium hover:bg-blue-700 transition-colors'
                : 'px-4 py-2 rounded-lg bg-gray-200 text-gray-700 font-medium hover:bg-gray-300 transition-colors';
        
        document.getElementById('listViewBtn').className = 
            view === 'list' 
                ? 'px-4 py-2 rounded-lg bg-blue-600 text-white font-medium hover:bg-blue-700 transition-colors'
                : 'px-4 py-2 rounded-lg bg-gray-200 text-gray-700 font-medium hover:bg-gray-300 transition-colors';

        // Show corresponding content
        if (view === 'overview') {
            document.getElementById('classOverviewContent').classList.remove('hidden');
            document.getElementById('studentListContent').classList.add('hidden');
        } else {
            document.getElementById('classOverviewContent').classList.add('hidden');
            document.getElementById('studentListContent').classList.remove('hidden');
        }
    }

    async checkAuth() {
        console.log('Checking authentication...');
        try {
            // For now, just show auth buttons
            this.showAuthButtons();
        } catch (error) {
            console.log('Auth check failed:', error);
            this.showAuthButtons();
        }
    }

    showUserInfo() {
        const userInfo = document.getElementById('userInfo');
        const authButtons = document.getElementById('authButtons');
        if (userInfo && authButtons) {
            userInfo.classList.remove('hidden');
            authButtons.classList.add('hidden');
        }
    }

    showAuthButtons() {
        const userInfo = document.getElementById('userInfo');
        const authButtons = document.getElementById('authButtons');
        if (userInfo && authButtons) {
            userInfo.classList.add('hidden');
            authButtons.classList.remove('hidden');
        }
    }

    async loadClasses() {
        try {
            console.log('Loading classes...');
            
            // 檢查是否有真實的 API 客戶端
            if (window.realAPIClient && window.realAPIClient.isAuthenticated) {
                console.log('🔗 使用真實 API 獲取班級列表...');
                const classes = await window.realAPIClient.getTeacherClasses();
                this.populateClassSelector(classes);
            } else {
                console.log('⚠️ 使用模擬數據 (真實 API 未認證)');
                // Mock data for testing
                const mockClasses = [
                    { id: 1, name: 'Class 7A', subject: 'Math' },
                    { id: 2, name: 'Class 7B', subject: 'English' },
                    { id: 3, name: 'Class 8A', subject: 'Science' }
                ];
                
                this.populateClassSelector(mockClasses);
            }
        } catch (error) {
            console.error('Failed to load classes:', error);
            this.showError('Failed to load class list');
        }
    }

    populateClassSelector(classes) {
        const selector = document.getElementById('classSelector');
        if (!selector) return;
        
        selector.innerHTML = '<option value="">Please select a class...</option>';
        
        classes.forEach(cls => {
            const option = document.createElement('option');
            option.value = cls.id;
            option.textContent = `${cls.name} (${cls.subject})`;
            selector.appendChild(option);
        });
        
        console.log('Class selector populated with', classes.length, 'classes');
        
        // Auto-select the first class if available
        if (classes.length > 0) {
            const firstClass = classes[0];
            selector.value = firstClass.id;
            this.currentClassId = firstClass.id;
            console.log('Auto-selected first class:', firstClass.name, 'with ID:', firstClass.id);
            
            // Trigger change event to load class data
            const event = new Event('change', { bubbles: true });
            selector.dispatchEvent(event);
        }
    }

    async loadClassOverview(classId) {
        try {
            this.showLoading();
            console.log('Loading class overview for class:', classId);
            
            // 檢查是否有真實的 API 客戶端
            if (window.realAPIClient && window.realAPIClient.isAuthenticated) {
                console.log('🔗 使用真實 API 獲取班級概覽...');
                const data = await window.realAPIClient.getClassOverview(classId);
                this.displayClassOverview(data);
            } else {
                console.log('⚠️ 使用模擬數據 (真實 API 未認證)');
                // Mock data
                const mockData = {
                    total_students: 25,
                    average_accuracy: 78.5,
                    average_speed: 45.2,
                    total_sessions: 150
                };
                
                this.displayClassOverview(mockData);
            }
        } catch (error) {
            console.error('Failed to load class overview:', error);
            this.showError('Failed to load class overview data');
        } finally {
            this.hideLoading();
        }
    }

    displayClassOverview(data) {
        console.log('Displaying class overview:', data);
        
        // Update statistics cards
        const totalStudents = document.getElementById('totalStudents');
        const averageAccuracy = document.getElementById('averageAccuracy');
        const averageSpeed = document.getElementById('averageSpeed');
        const totalSessions = document.getElementById('totalSessions');

        if (totalStudents) totalStudents.textContent = data.total_students || 0;
        if (averageAccuracy) averageAccuracy.textContent = `${(data.average_accuracy || 0).toFixed(1)}%`;
        if (averageSpeed) averageSpeed.textContent = `${(data.average_speed || 0).toFixed(1)} sec/question`;
        if (totalSessions) totalSessions.textContent = data.total_sessions || 0;

        // Show content
        this.showContent();
    }

    async loadStudents(classId) {
        try {
            this.showLoading();
            console.log('Loading students for class:', classId);
            
            // 檢查是否有真實的 API 客戶端
            if (window.realAPIClient && window.realAPIClient.isAuthenticated) {
                console.log('🔗 使用真實 API 獲取學生列表...');
                const data = await window.realAPIClient.getClassStudentsAnalysis(classId, this.currentPage, this.pageSize);
                
                this.students = data.students || [];
                this.totalCount = data.total_count || 0;
                this.totalPages = data.total_pages || 0;
                this.currentPage = data.page || 1;
            } else {
                console.log('⚠️ 使用模擬數據 (真實 API 未認證)');
                // Mock data
                const mockStudents = [
                    { student_id: 1, student_name: 'John Doe', class_name: 'Class 7A', accuracy_rate: 85.5, average_speed: 35.2, total_sessions: 12, total_questions: 120, last_active: new Date() },
                    { student_id: 2, student_name: 'Jane Smith', class_name: 'Class 7A', accuracy_rate: 72.3, average_speed: 52.1, total_sessions: 8, total_questions: 80, last_active: new Date(Date.now() - 86400000) },
                    { student_id: 3, student_name: 'Bob Johnson', class_name: 'Class 7A', accuracy_rate: 91.2, average_speed: 28.5, total_sessions: 15, total_questions: 150, last_active: new Date() }
                ];
                
                this.students = mockStudents;
                this.totalCount = mockStudents.length;
                this.totalPages = 1;
                this.currentPage = 1;
            }
            
            this.filterAndDisplayStudents();
            this.updateStatistics();
            this.updatePagination();
        } catch (error) {
            console.error('Failed to load students:', error);
            this.showError('Failed to load student data');
        } finally {
            this.hideLoading();
        }
    }

    filterAndDisplayStudents() {
        // Search filter
        this.filteredStudents = this.students.filter(student => 
            student.student_name.toLowerCase().includes(this.searchTerm)
        );

        this.displayStudents();
    }

    displayStudents() {
        const grid = document.getElementById('studentGrid');
        if (!grid) return;
        
        grid.innerHTML = '';

        if (this.filteredStudents.length === 0) {
            grid.innerHTML = `
                <div class="col-span-full text-center py-12 text-gray-500">
                    <span class="material-icons text-4xl text-gray-300 mb-2">search_off</span>
                    <p>No students found matching criteria</p>
                </div>
            `;
            return;
        }

        this.filteredStudents.forEach(student => {
            const card = this.createStudentCard(student);
            grid.appendChild(card);
        });
    }

    createStudentCard(student) {
        const card = document.createElement('div');
        card.className = 'bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow cursor-pointer';
        card.addEventListener('click', () => this.openStudentDetail(student.student_id));

        card.innerHTML = `
            <div class="flex items-center justify-between mb-4">
                <div class="flex items-center space-x-3">
                    <div class="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                        <span class="material-icons text-blue-600">person</span>
                    </div>
                    <div>
                        <h3 class="font-semibold text-gray-800">${student.student_name}</h3>
                        <p class="text-sm text-gray-500">${student.class_name}</p>
                    </div>
                </div>
                <div class="text-right">
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        Active
                    </span>
                </div>
            </div>

            <div class="space-y-3">
                <div>
                    <div class="flex justify-between text-sm mb-1">
                        <span class="text-gray-600">Accuracy Rate</span>
                        <span class="font-medium">${(student.accuracy_rate || 0).toFixed(1)}%</span>
                    </div>
                    <div class="w-full bg-gray-200 rounded-full h-2">
                        <div class="h-2 rounded-full bg-green-500" style="width: ${Math.min(student.accuracy_rate || 0, 100)}%"></div>
                    </div>
                </div>

                <div>
                    <div class="flex justify-between text-sm mb-1">
                        <span class="text-gray-600">Answer Speed</span>
                        <span class="font-medium">${student.average_speed || 0} sec/question</span>
                    </div>
                    <div class="w-full bg-gray-200 rounded-full h-2">
                        <div class="h-2 rounded-full bg-green-500" style="width: ${Math.min((student.average_speed || 0) / 2, 100)}%"></div>
                    </div>
                </div>

                <div class="grid grid-cols-2 gap-4 pt-3 border-t border-gray-100">
                    <div class="text-center">
                        <p class="text-lg font-bold text-blue-600">${student.total_sessions || 0}</p>
                        <p class="text-xs text-gray-500">Learning Sessions</p>
                    </div>
                    <div class="text-center">
                        <p class="text-lg font-bold text-green-600">${student.total_questions || 0}</p>
                        <p class="text-xs text-gray-500">Total Questions</p>
                    </div>
                </div>
            </div>
        `;

        return card;
    }

    updateStatistics() {
        if (this.students.length === 0) return;

        const totalStudents = this.students.length;
        const avgAccuracy = this.students.reduce((sum, s) => sum + (s.accuracy_rate || 0), 0) / totalStudents;
        const avgSpeed = this.students.reduce((sum, s) => sum + (s.average_speed || 0), 0) / totalStudents;

        // Update statistics summary
        const totalStudentsEl = document.getElementById('totalStudents');
        const averageAccuracyEl = document.getElementById('averageAccuracy');
        const averageSpeedEl = document.getElementById('averageSpeed');

        if (totalStudentsEl) totalStudentsEl.textContent = totalStudents;
        if (averageAccuracyEl) averageAccuracyEl.textContent = `${avgAccuracy.toFixed(1)}%`;
        if (averageSpeedEl) averageSpeedEl.textContent = `${avgSpeed.toFixed(1)} sec/question`;
    }

    updatePagination() {
        const startIndex = (this.currentPage - 1) * this.pageSize + 1;
        const endIndex = Math.min(this.currentPage * this.pageSize, this.totalCount);

        const startIndexEl = document.getElementById('startIndex');
        const endIndexEl = document.getElementById('endIndex');
        const totalCountEl = document.getElementById('totalCount');

        if (startIndexEl) startIndexEl.textContent = startIndex;
        if (endIndexEl) endIndexEl.textContent = endIndex;
        if (totalCountEl) totalCountEl.textContent = this.totalCount;
    }

    openStudentDetail(studentId) {
        console.log('Opening student detail for:', studentId);
        // For now, just log the action
        alert(`Student detail for ID: ${studentId} - Feature coming soon!`);
    }

    // State management methods
    showLoading() {
        const loadingIndicator = document.getElementById('loadingIndicator');
        const classOverviewContent = document.getElementById('classOverviewContent');
        const studentListContent = document.getElementById('studentListContent');
        const noDataState = document.getElementById('noDataState');
        const errorState = document.getElementById('errorState');

        if (loadingIndicator) loadingIndicator.classList.remove('hidden');
        if (classOverviewContent) classOverviewContent.classList.add('hidden');
        if (studentListContent) studentListContent.classList.add('hidden');
        if (noDataState) noDataState.classList.add('hidden');
        if (errorState) errorState.classList.add('hidden');
    }

    hideLoading() {
        const loadingIndicator = document.getElementById('loadingIndicator');
        if (loadingIndicator) loadingIndicator.classList.add('hidden');
    }

    showContent() {
        const classOverviewContent = document.getElementById('classOverviewContent');
        const noDataState = document.getElementById('noDataState');
        const errorState = document.getElementById('errorState');

        if (classOverviewContent) classOverviewContent.classList.remove('hidden');
        if (noDataState) noDataState.classList.add('hidden');
        if (errorState) errorState.classList.add('hidden');
    }

    showNoDataState() {
        const classOverviewContent = document.getElementById('classOverviewContent');
        const studentListContent = document.getElementById('studentListContent');
        const noDataState = document.getElementById('noDataState');
        const errorState = document.getElementById('errorState');

        if (classOverviewContent) classOverviewContent.classList.add('hidden');
        if (studentListContent) studentListContent.classList.add('hidden');
        if (noDataState) noDataState.classList.remove('hidden');
        if (errorState) errorState.classList.add('hidden');
    }

    showError(message) {
        const errorMessage = document.getElementById('errorMessage');
        const classOverviewContent = document.getElementById('classOverviewContent');
        const studentListContent = document.getElementById('studentListContent');
        const noDataState = document.getElementById('noDataState');
        const errorState = document.getElementById('errorState');

        if (errorMessage) errorMessage.textContent = message;
        if (classOverviewContent) classOverviewContent.classList.add('hidden');
        if (studentListContent) studentListContent.classList.add('hidden');
        if (noDataState) noDataState.classList.add('hidden');
        if (errorState) errorState.classList.remove('hidden');
    }
}

// Global variable for backward compatibility
window.StudentsAnalysisManager = StudentsAnalysisManager;

console.log('StudentsAnalysisManager loaded successfully');
