function historyComponent() {
  return {
    // Main data
    historyData: null,
    days: 30,
    
    // Derived data
    progressEntries: [],
    totalTasksCompleted: 0,
    totalXpEarned: 0,
    averageCompletion: 0,
    
    // Calendar organization
    weeks: [],
    
    // Modal state
    showDayDetail: false,
    selectedDate: null,
    dayDetailData: null,
    
    // Loading states
    isLoading: false,
    isLoadingDetail: false,
    error: null,
    
    // Load history data
    async loadHistory() {
      this.isLoading = true;
      this.error = null;
      
      try {
        const response = await fetch(`/api/history?user_id=1&days=${this.days}`);
        
        if (!response.ok) {
          throw new Error('Failed to load history');
        }
        
        this.historyData = await response.json();
        console.log('📊 History data received:', this.historyData);
        
        this.progressEntries = this.historyData.progress_entries || [];
        console.log('📅 Progress entries:', this.progressEntries.length, 'entries');
        
        this.totalTasksCompleted = this.historyData.total_tasks_completed;
        this.totalXpEarned = this.historyData.total_xp_earned;
        this.averageCompletion = this.historyData.average_completion;
        
        // Organize into calendar weeks
        this.organizeIntoWeeks();
        
      } catch (err) {
        this.error = err.message || 'Failed to load history';
        console.error('❌ History load error:', err);
      } finally {
        this.isLoading = false;
      }
    },
    
    // Load detail data for specific day
    async loadDayDetail(dateStr) {
      this.isLoadingDetail = true;
      this.selectedDate = dateStr;
      this.showDayDetail = true;
      this.dayDetailData = null;
      
      try {
        const response = await fetch(`/api/history/${dateStr}?user_id=1`);
        
        if (!response.ok) {
          throw new Error('Failed to load day details');
        }
        
        this.dayDetailData = await response.json();
        
      } catch (err) {
        this.error = err.message || 'Failed to load day details';
        console.error('Day detail load error:', err);
      } finally {
        this.isLoadingDetail = false;
      }
    },
    
    // Organize progress entries into calendar weeks
    organizeIntoWeeks() {
      if (!this.progressEntries || this.progressEntries.length === 0) {
        this.weeks = [];
        return;
      }
      
      const weeks = [];
      let currentWeek = [];
      
      // Parse first date reliably (handle YYYY-MM-DD format)
      const firstDateStr = this.progressEntries[0].date;
      const [year, month, day] = firstDateStr.split('-').map(Number);
      const firstDate = new Date(year, month - 1, day);
      const firstDayOfWeek = firstDate.getDay();
      
      // Add empty cells for offset (days before start_date)
      for (let i = 0; i < firstDayOfWeek; i++) {
        currentWeek.push(null);
      }
      
      // Add each day from progress entries
      this.progressEntries.forEach(entry => {
        currentWeek.push(entry);
        
        // When week is full (7 days), start new week
        if (currentWeek.length === 7) {
          weeks.push([...currentWeek]);
          currentWeek = [];
        }
      });
      
      // Add remaining days in last incomplete week
      if (currentWeek.length > 0) {
        while (currentWeek.length < 7) {
          currentWeek.push(null);
        }
        weeks.push(currentWeek);
      }
      
      this.weeks = weeks;
      console.log('Organized into weeks:', weeks.length, 'weeks with', this.progressEntries.length, 'total entries');
    },
    
    // Get color class based on completion percentage
    getCompletionColor(percentage) {
      if (percentage === 0) return 'bg-gray-200';
      if (percentage >= 90) return 'bg-green-500';
      if (percentage >= 50) return 'bg-yellow-500';
      return 'bg-red-400';
    },
    
    // Format date for display
    formatDate(dateStr) {
      const date = new Date(dateStr);
      return date.toLocaleDateString('en-US', { 
        weekday: 'long',
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
      });
    },
    
    // Close day detail modal
    closeDayDetail() {
      this.showDayDetail = false;
      this.selectedDate = null;
      this.dayDetailData = null;
    }
  }
}