function taskFormComponent(mode = 'create', existingTask = null) {
  return {
    mode: mode,
    existingTask: existingTask,
    
    formData: {
      title: existingTask?.title || '',
      description: existingTask?.description || '',
      priority: existingTask?.priority || 'medium',
      urgency: existingTask?.urgency || 'medium',
      due_date: existingTask?.due_date || (mode === 'create' ? new Date(new Date().getTime() - new Date().getTimezoneOffset() * 60000).toISOString().slice(0, 16) : null),
      recurrence_pattern: existingTask?.recurrence_pattern || 'none',
      recurrence_rule_on_complete: existingTask?.recurrence_rule_on_complete || false,
      custom_xp: existingTask?.custom_xp || null
    },
    
    errors: {},
    isSubmitting: false,
    submitSuccess: false,
    submitError: null,
    showCustomXp: existingTask?.custom_xp !== null,
    
    // Character counters
    get titleLength() {
      return this.formData.title?.length || 0;
    },
    
    get descriptionLength() {
      return this.formData.description?.length || 0;
    },
    
    // XP calculation
    get calculatedXp() {
      if (this.formData.custom_xp !== null && this.formData.custom_xp !== '') {
        return parseInt(this.formData.custom_xp);
      }
      
      const priorityXp = {'low': 5, 'medium': 10, 'high': 15};
      const urgencyXp = {'low': 5, 'medium': 10, 'high': 15};
      
      return priorityXp[this.formData.priority] + urgencyXp[this.formData.urgency];
    },
    
    get xpBreakdown() {
      if (this.formData.custom_xp !== null && this.formData.custom_xp !== '') {
        return `Custom XP: ${this.formData.custom_xp} XP`;
      }
      
      const pXp = {'low': 5, 'medium': 10, 'high': 15}[this.formData.priority];
      const uXp = {'low': 5, 'medium': 10, 'high': 15}[this.formData.urgency];
      
      return `Priority: ${pXp} + Urgency: ${uXp} = ${this.calculatedXp} XP`;
    },
    
    // Computed properties for dual-mode
    get isEditMode() {
      return this.mode === 'edit';
    },
    
    get submitButtonText() {
      if (this.isSubmitting) return this.isEditMode ? 'Saving...' : 'Creating...';
      return this.isEditMode ? 'Save Changes' : 'Create Task';
    },
    
    get submitUrl() {
      return this.isEditMode 
        ? `/api/tasks/${this.existingTask.id}` 
        : '/api/tasks';
    },
    
    get submitMethod() {
      return this.isEditMode ? 'PUT' : 'POST';
    },
    
    // Validation
    validateForm() {
      this.errors = {};
      
      // Title validation
      if (!this.formData.title || this.formData.title.trim() === '') {
        this.errors.title = 'Title is required';
      } else if (this.formData.title.length > 255) {
        this.errors.title = 'Title must be 255 characters or less';
      }
      
      // Description validation
      if (this.formData.description && this.formData.description.length > 1000) {
        this.errors.description = 'Description must be 1000 characters or less';
      }
      
      // Custom XP validation
      if (this.formData.custom_xp !== null && this.formData.custom_xp < 0) {
        this.errors.custom_xp = 'XP cannot be negative';
      }
      
      // Due date validation
      if (this.formData.due_date) {
        const dueDate = new Date(this.formData.due_date);
        const now = new Date();
        if (dueDate < now) {
          this.errors.due_date = 'Due date cannot be in the past';
        }
      }
      
      return Object.keys(this.errors).length === 0;
    },
    
    // Form submission
    async submitForm() {
      // Validate first
      if (!this.validateForm()) {
        return;
      }
      
      this.isSubmitting = true;
      this.submitError = null;
      
      try {
        const response = await fetch(this.submitUrl, {
          method: this.submitMethod,
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(this.formData)
        });
        
        if (!response.ok) {
          const error = await response.json();
          
          // Handle validation errors from server
          if (error.detail && Array.isArray(error.detail)) {
            error.detail.forEach(err => {
              const field = err.loc[err.loc.length - 1];
              this.errors[field] = err.msg;
            });
          } else {
            this.submitError = error.detail || 'Failed to save task';
          }
          return;
        }
        
        const task = await response.json();
        
        // Success!
        this.submitSuccess = true;
        
        if (this.isEditMode) {
          // Close modal and refresh task list
          this.$dispatch('task-updated', task);
        } else {
          // Add to task list and reset form
          this.$dispatch('task-created', task);
          this.resetForm();
          
          // Show success message briefly
          setTimeout(() => {
            this.submitSuccess = false;
          }, 3000);
        }
        
      } catch (error) {
        console.error('Form submission error:', error);
        this.submitError = 'Network error. Please try again.';
      } finally {
        this.isSubmitting = false;
      }
    },
    
    // Form reset
    resetForm() {
      this.formData = {
        title: '',
        description: '',
        priority: 'medium',
        urgency: 'medium',
        due_date: null,
        recurrence_pattern: 'none',
        recurrence_rule_on_complete: false,
        custom_xp: null
      };
      this.errors = {};
      this.showCustomXp = false;
    },
    
    // Cancel action
    cancel() {
      if (this.isEditMode) {
        this.$dispatch('close-edit-modal');
      } else {
        this.resetForm();
      }
    }
  }
}