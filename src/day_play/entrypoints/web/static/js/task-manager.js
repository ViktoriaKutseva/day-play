function taskManagerComponent() {
  return {
    // State
    tasks: [],
    loading: true,
    error: null,
    
    // Filters
    statusFilter: 'all',
    priorityFilter: 'all',
    urgencyFilter: 'all',
    dateFromFilter: '',
    dateToFilter: '',
    
    // UI State
    showEditModal: false,
    showDeleteModal: false,
    selectedTask: null,
    taskToDelete: null,
    
    // Edit Form
    editForm: {
      title: '',
      description: '',
      priority: 'medium',
      urgency: 'medium',
      due_date: ''
    },
    
    // Pagination
    currentPage: 1,
    tasksPerPage: 10,
    
    // Computed Properties
    get filteredTasks() {
      let result = this.tasks;
      
      if (this.statusFilter !== 'all') {
        result = result.filter(task => task.status === this.statusFilter);
      }
      
      if (this.priorityFilter !== 'all') {
        result = result.filter(task => task.priority === this.priorityFilter);
      }
      
      if (this.urgencyFilter !== 'all') {
        result = result.filter(task => task.urgency === this.urgencyFilter);
      }
      
      if (this.dateFromFilter) {
        const fromDate = new Date(this.dateFromFilter);
        result = result.filter(task => {
          if (!task.due_date) return false;
          return new Date(task.due_date) >= fromDate;
        });
      }
      
      if (this.dateToFilter) {
        const toDate = new Date(this.dateToFilter);
        result = result.filter(task => {
          if (!task.due_date) return false;
          return new Date(task.due_date) <= toDate;
        });
      }
      
      return result;
    },
    
    get paginatedTasks() {
      const start = (this.currentPage - 1) * this.tasksPerPage;
      const end = start + this.tasksPerPage;
      return this.filteredTasks.slice(start, end);
    },
    
    get taskStats() {
      return {
        total: this.filteredTasks.length,
        active: this.filteredTasks.filter(t => t.status === 'pending').length,
        completed: this.filteredTasks.filter(t => t.status === 'completed').length
      };
    },
    
    get hasActiveFilters() {
      return this.statusFilter !== 'all' 
        || this.priorityFilter !== 'all'
        || this.urgencyFilter !== 'all'
        || this.dateFromFilter !== ''
        || this.dateToFilter !== '';
    },
    
    get totalPages() {
      return Math.ceil(this.filteredTasks.length / this.tasksPerPage);
    },

    // Priority-Urgency Matrix Groupings
    priorityScores: { 'high': 3, 'medium': 2, 'low': 1 },
    urgencyScores: { 'high': 3, 'medium': 2, 'low': 1 },
    calculateTaskScore(task) {
      return this.priorityScores[task.priority] + this.urgencyScores[task.urgency];
    },

    get sortedTasksByPriorityUrgency() {
      return this.filteredTasks.slice().sort((a, b) => {
        return this.calculateTaskScore(b) - this.calculateTaskScore(a);
      });
    },
    // Critical tasks (score = 6)
    get criticalTasks() {
      return this.filteredTasks.filter(task => 
        this.calculateTaskScore(task) === 6
      );
    },

    // High priority tasks (scores 4-5)
    get highTasks() {
      return this.filteredTasks.filter(task => {
        const score = this.calculateTaskScore(task);
        return score >= 4 && score <= 5;
      });
    },

    // Medium priority tasks (score = 3)
    get mediumTasks() {
      return this.filteredTasks.filter(task => 
        this.calculateTaskScore(task) === 3
      );
    },

    // Low priority tasks (score = 2)
    get lowTasks() {
      return this.filteredTasks.filter(task => 
        this.calculateTaskScore(task) === 2
      );
    },
    // get highPriorityHighUrgencyTasks() {
    //   return this.filteredTasks.filter(task =>
    //     task.priority === 'high' && task.urgency === 'high'
    //   );
    // },

    // get highPriorityLowUrgencyTasks() {
    //   return this.filteredTasks.filter(task =>
    //     task.priority === 'high' && task.urgency === 'low'
    //   );
    // },

    // get lowPriorityHighUrgencyTasks() {
    //   return this.filteredTasks.filter(task =>
    //     task.priority === 'low' && task.urgency === 'high'
    //   );
    // },

    // get lowPriorityLowUrgencyTasks() {
    //   return this.filteredTasks.filter(task =>
    //     task.priority === 'low' && task.urgency === 'low'
    //   );
    // },

    // Lifecycle
    async init() {
      await this.loadTasks();
    },
    
    // Data Operations
    async loadTasks() {
      try {
        this.loading = true;
        this.error = null;
        
        const response = await fetch('/api/tasks?user_id=1');
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        this.tasks = await response.json();
        this.loading = false;
      } catch (error) {
        console.error('Failed to load tasks:', error);
        this.error = 'Failed to load tasks. Please try again.';
        this.loading = false;
      }
    },
    
    // Filter Operations
    resetFilters() {
      this.statusFilter = 'all';
      this.priorityFilter = 'all';
      this.urgencyFilter = 'all';
      this.dateFromFilter = '';
      this.dateToFilter = '';
      this.currentPage = 1;
    },
    
    // Task Actions
    async toggleTaskComplete(task) {
      const previousStatus = task.status;
      const previousUpdatedAt = task.updated_at;
      
      // Optimistic update
      task.status = task.status === 'completed' ? 'pending' : 'completed';
      task.updated_at = new Date().toISOString();
      
      try {
        const endpoint = task.status === 'completed' 
          ? `/api/tasks/${task.id}/complete`
          : `/api/tasks/${task.id}/undo`;
        
        const response = await fetch(endpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        });
        
        if (!response.ok) throw new Error('Failed to update task');
        
        const updatedTask = await response.json();
        Object.assign(task, updatedTask);
        
      } catch (error) {
        console.error('Failed to toggle task completion:', error);
        task.status = previousStatus;
        task.updated_at = previousUpdatedAt;
        this.error = 'Failed to update task. Please try again.';
        setTimeout(() => { this.error = null; }, 3000);
      }
    },
    
    openEditModal(task) {
      this.selectedTask = task;
      this.editForm = {
        title: task.title,
        description: task.description || '',
        priority: task.priority,
        urgency: task.urgency,
        due_date: task.due_date ? task.due_date.slice(0, 16) : ''
      };
      this.showEditModal = true;
    },
    
    closeEditModal() {
      this.showEditModal = false;
      this.selectedTask = null;
      this.editForm = {
        title: '',
        description: '',
        priority: 'medium',
        urgency: 'medium',
        due_date: ''
      };
    },
    
    async saveTask() {
      if (!this.editForm.title.trim()) {
        this.error = 'Task title is required';
        return;
      }
      
      try {
        this.loading = true;
        
        const response = await fetch(`/api/tasks/${this.selectedTask.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            title: this.editForm.title,
            description: this.editForm.description,
            priority: this.editForm.priority,
            urgency: this.editForm.urgency,
            due_date: this.editForm.due_date || null
          })
        });
        
        if (!response.ok) throw new Error('Failed to update task');
        
        const updatedTask = await response.json();
        const index = this.tasks.findIndex(t => t.id === updatedTask.id);
        if (index !== -1) {
          this.tasks[index] = updatedTask;
        }
        
        this.closeEditModal();
        this.loading = false;
        
      } catch (error) {
        console.error('Failed to save task:', error);
        this.error = 'Failed to save task. Please try again.';
        this.loading = false;
      }
    },
    
    confirmDelete(task) {
      this.taskToDelete = task;
      this.showDeleteModal = true;
    },
    
    cancelDelete() {
      this.showDeleteModal = false;
      this.taskToDelete = null;
    },
    
    async deleteTask() {
      if (!this.taskToDelete) return;
      
      const taskId = this.taskToDelete.id;
      
      try {
        this.loading = true;
        
        const response = await fetch(`/api/tasks/${taskId}`, {
          method: 'DELETE'
        });
        
        if (!response.ok) throw new Error('Failed to delete task');
        
        this.tasks = this.tasks.filter(t => t.id !== taskId);
        this.showDeleteModal = false;
        this.taskToDelete = null;
        this.loading = false;
        
      } catch (error) {
        console.error('Failed to delete task:', error);
        this.error = 'Failed to delete task. Please try again.';
        this.loading = false;
      }
    }
  }
}