// Settings page Alpine.js component
function settingsComponent() {
    return {
        // Data
        availablePrizes: [],
        redeemedPrizes: [],
        userTotalXP: 0,
        loading: true,
        error: null,
        showCreateForm: false,
        showRedeemModal: false,
        prizeToRedeem: null,

        // Form data
        newPrize: {
            name: '',
            description: '',
            cost_xp: 0
        },

        // Preferences (local storage for now)
        preferences: {
            notifications: true,
            defaultView: 'dashboard',
            theme: 'light'
        },

        // Computed
        get canAffordAnyPrize() {
            return this.availablePrizes.some(prize => prize.cost_xp <= this.userTotalXP);
        },

        get totalPrizeValue() {
            return this.redeemedPrizes.reduce((sum, prize) => sum + prize.cost_xp, 0);
        },

        // Methods
        async init() {
            await this.loadPreferences();
            await this.loadData();
        },

        async loadData() {
            try {
                this.loading = true;
                this.error = null;

                // Load user XP
                const userResponse = await fetch('/api/user/level');
                if (!userResponse.ok) throw new Error('Failed to load user data');
                const userData = await userResponse.json();
                this.userTotalXP = userData.total_xp;

                // Load prizes
                const prizesResponse = await fetch('/api/gamification/prizes?is_redeemed=false');
                if (!prizesResponse.ok) throw new Error('Failed to load available prizes');
                this.availablePrizes = await prizesResponse.json();

                const redeemedResponse = await fetch('/api/gamification/prizes?is_redeemed=true');
                if (!redeemedResponse.ok) throw new Error('Failed to load redeemed prizes');
                this.redeemedPrizes = await redeemedResponse.json();

            } catch (error) {
                this.error = error.message;
                console.error('Error loading settings data:', error);
            } finally {
                this.loading = false;
            }
        },

        async loadPreferences() {
            const saved = localStorage.getItem('dayPlayPreferences');
            if (saved) {
                try {
                    this.preferences = { ...this.preferences, ...JSON.parse(saved) };
                } catch (e) {
                    console.warn('Failed to parse saved preferences');
                }
            }
        },

        savePreferences() {
            localStorage.setItem('dayPlayPreferences', JSON.stringify(this.preferences));
            this.error = '✅ Preferences saved successfully!';
            setTimeout(() => this.error = null, 3000);
        },

        resetPreferences() {
            this.preferences = {
                notifications: true,
                defaultView: 'dashboard',
                theme: 'light'
            };
            localStorage.removeItem('dayPlayPreferences');
        },

        toggleCreateForm() {
            this.showCreateForm = !this.showCreateForm;
            if (!this.showCreateForm) {
                this.resetNewPrizeForm();
            }
        },

        resetNewPrizeForm() {
            this.newPrize = {
                name: '',
                description: '',
                cost_xp: 0
            };
        },

        async createPrize() {
            if (!this.newPrize.name.trim() || this.newPrize.cost_xp <= 0) {
                this.error = 'Please fill in all required fields with valid values.';
                return;
            }

            try {
                const response = await fetch('/api/gamification/prizes', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(this.newPrize)
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || 'Failed to create prize');
                }

                const newPrize = await response.json();
                this.availablePrizes.push(newPrize);
                this.resetNewPrizeForm();
                this.showCreateForm = false;
                this.error = '✅ Prize created successfully!';

            } catch (error) {
                this.error = error.message;
                console.error('Error creating prize:', error);
            }
        },

        async redeemPrize(prize) {
            this.prizeToRedeem = prize;
            this.showRedeemModal = true;
        },

        closeRedeemModal() {
            this.showRedeemModal = false;
            this.prizeToRedeem = null;
        },

        async confirmRedemption() {
            if (!this.prizeToRedeem) return;

            try {
                const response = await fetch(`/api/gamification/prizes/${this.prizeToRedeem.id}/redeem`, {
                    method: 'POST'
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || 'Failed to redeem prize');
                }

                const redeemedPrize = await response.json();

                // Move prize from available to redeemed
                this.availablePrizes = this.availablePrizes.filter(p => p.id !== this.prizeToRedeem.id);
                this.redeemedPrizes.push(redeemedPrize);

                this.closeRedeemModal();
                this.error = '🎉 Prize redeemed successfully!';

            } catch (error) {
                this.error = error.message;
                console.error('Error redeeming prize:', error);
            }
        },

        formatXP(xp) {
            return new Intl.NumberFormat().format(xp);
        }
    }
}