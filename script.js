class TrashKartGame {
    constructor() {
        this.gameId = null;
        this.playerId = this.generatePlayerId();
        this.gameState = null;
        this.isPlaying = false;
        this.isAlive = true;
        this.bestScore = 0;
        this.currentScore = 0;
        this.boostCharges = 3;
        this.keysPressed = {};
        this.touchControls = {};
        this.renderInterval = null;
        this.gameLoopInterval = null;
        this.canvas = document.getElementById('game-canvas');
        this.ctx = this.canvas.getContext('2d');
        
        this.initTelegramWebApp();
        this.bindEvents();
        this.loadBestScore();
        this.showScreen('main-menu');
    }
    
    generatePlayerId() {
        return 'player_' + Math.random().toString(36).substr(2, 9);
    }
    
    initTelegramWebApp() {
        if (window.Telegram && Telegram.WebApp) {
            Telegram.WebApp.ready();
            Telegram.WebApp.expand();
            Telegram.WebApp.enableClosingConfirmation();
            
            this.playerId = Telegram.WebApp.initDataUnsafe.user?.id || this.playerId;
            
            // Установка цвета темы
            Telegram.WebApp.setBackgroundColor('#1a1a2e');
            Telegram.WebApp.setHeaderColor('#1a1a2e');
        }
    }
    
    bindEvents() {
        // Навигация по меню
        document.getElementById('btn-play').addEventListener('click', () => this.startNewGame());
        document.getElementById('btn-controls').addEventListener('click', () => this.showScreen('controls-screen'));
        document.getElementById('btn-back-from-controls').addEventListener('click', () => this.showScreen('main-menu'));
        document.getElementById('btn-about').addEventListener('click', () => this.showAbout());
        
        // Управление в игре
        document.getElementById('btn-brake').addEventListener('touchstart', (e) => {
            e.preventDefault();
            this.touchControls.brake = true;
            this.sendAction('brake');
        });
        document.getElementById('btn-brake').addEventListener('touchend', (e) => {
            e.preventDefault();
            this.touchControls.brake = false;
        });
        
        document.getElementById('btn-gas').addEventListener('touchstart', (e) => {
            e.preventDefault();
            this.touchControls.gas = true;
            this.sendAction('gas');
        });
        document.getElementById('btn-gas').addEventListener('touchend', (e) => {
            e.preventDefault();
            this.touchControls.gas = false;
        });
        
        document.getElementById('btn
