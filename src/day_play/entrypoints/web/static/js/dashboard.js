
function dashboardComponent() {
  // Keep existing dashboardComponent code (lines 645-738)
}
function dashboardComponent() {
  return {
    // State
    loading: true,
    error: null,
    dailyProgress: 0,
    levelProgress: 0,
    level: 1,
    currentXP: 0,
    nextLevelXP: 100,
    tasks: [],
    achievements: [],
    newTaskTitle: '',
    taskAdded: false,
    showCreateModal: false,
    
    // Initialize - runs when component loads
    async init() {
      try {
        this.loading = true;
        this.error = null;
        
        const response = await fetch('/api/dashboard?user_id=1');
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Update state with API data
        this.dailyProgress = data.progress.daily_completion_percent;
        this.levelProgress = data.progress.level_progress_percent;
        this.level = data.user_level.current_level;
        this.currentXP = data.user_level.total_xp;
        this.nextLevelXP = data.user_level.xp_for_next_level;
        this.tasks = data.upcoming_tasks;
        this.achievements = data.recent_achievements;
        
        this.loading = false;
      } catch (error) {
        console.error('Failed to load dashboard:', error);
        this.error = 'Failed to load dashboard data. Please refresh the page.';
        this.loading = false;
      }
    },
    
    // Add new task
    async addTask() {
      if (!this.newTaskTitle.trim()) return;
      
      try {
        this.loading = true;
        
        const response = await fetch('/api/tasks', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            title: this.newTaskTitle,
            priority: 'medium',
            urgency: 'medium',
            status: 'pending'
          })
        });
        
        if (!response.ok) throw new Error('Failed to create task');
        
        const newTask = await response.json();
        this.tasks.push(newTask);
        this.newTaskTitle = '';
        this.taskAdded = true;
        this.showCreateModal = false;
        
        setTimeout(() => { 
          this.taskAdded = false; 
        }, 3000);
        
        // Reload dashboard to refresh progress
        await this.init();
        
      } catch (error) {
        console.error('Failed to add task:', error);
        this.error = 'Failed to add task. Please try again.';
        this.loading = false;
      }
    }
  }
}