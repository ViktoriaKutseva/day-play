
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

    closeModal() {
      this.showCreateModal = false;
    },

    async completeTask(taskId) {
      try {
        const response = await fetch(`/api/tasks/${taskId}/complete`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        });
        
        if (!response.ok) throw new Error('Failed to complete task');
        
        // Refresh dashboard to update progress and level
        await this.init();
      } catch (error) {
        console.error('Failed to complete task:', error);
        this.error = 'Failed to complete task. Please try again.';
      }
    },

    async undoTask(taskId) {
      try {
        const response = await fetch(`/api/tasks/${taskId}/undo`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        });
        
        if (!response.ok) throw new Error('Failed to undo task');
        
        // Refresh dashboard to update progress and level
        await this.init();
      } catch (error) {
        console.error('Failed to undo task:', error);
        this.error = 'Failed to undo task. Please try again.';
      }
    }
  }
}