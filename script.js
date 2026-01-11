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
        
        document.getElementById('btn-boost').addEventListener('touchstart', (e) => {
            e.preventDefault();
            if (this.boostCharges > 0) {
                this.sendAction('boost');
                this.boostCharges--;
                this.updateBoostDisplay();
            }
        });
        
        // Клавиатурное управление
        document.addEventListener('keydown', (e) => {
            if (!this.isPlaying) return;
            
            switch(e.key.toLowerCase()) {
                case 'a':
                    e.preventDefault();
                    this.keysPressed.brake = true;
                    this.sendAction('brake');
                    break;
                case 's':
                    e.preventDefault();
                    this.keysPressed.gas = true;
                    this.sendAction('gas');
                    break;
                case ' ':
                    e.preventDefault();
                    if (this.boostCharges > 0) {
                        this.sendAction('boost');
                        this.boostCharges--;
                        this.updateBoostDisplay();
                    }
                    break;
                case 'escape':
                    e.preventDefault();
                    this.togglePause();
                    break;
            }
        });
        
        document.addEventListener('keyup', (e) => {
            switch(e.key.toLowerCase()) {
                case 'a':
                    this.keysPressed.brake = false;
                    break;
                case 's':
                    this.keysPressed.gas = false;
                    break;
            }
        });
        
        // Управление игрой
        document.getElementById('btn-pause').addEventListener('click', () => this.togglePause());
        document.getElementById('btn-restart').addEventListener('click', () => this.restartGame());
        document.getElementById('btn-menu').addEventListener('click', () => this.returnToMenu());
        
        document.getElementById('btn-resume').addEventListener('click', () => this.togglePause());
        document.getElementById('btn-restart-from-pause').addEventListener('click', () => this.restartGame());
        document.getElementById('btn-menu-from-pause').addEventListener('click', () => this.returnToMenu());
        
        document.getElementById('btn-restart-after-death').addEventListener('click', () => this.restartGame());
        document.getElementById('btn-menu-after-death').addEventListener('click', () => this.returnToMenu());
    }
    
    async startNewGame() {
        try {
            this.showScreen('game-screen');
            this.isPlaying = true;
            this.isAlive = true;
            this.currentScore = 0;
            this.boostCharges = 3;
            this.updateBoostDisplay();
            
            // Показываем сообщение "ГОТОВ?"
            const messageEl = document.getElementById('game-message');
            messageEl.textContent = 'ГОТОВ?';
            messageEl.style.display = 'block';
            
            // Создаем новую игру на сервере
            const response = await fetch('/api/game/new', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ player_id: this.playerId })
            });
            
            const data = await response.json();
            this.gameId = data.game_id;
            
            // Обновляем отображение рекорда
            document.getElementById('current-best').textContent = this.bestScore;
            
            // Запускаем игровой цикл
            setTimeout(() => {
                messageEl.style.display = 'none';
                this.startGameLoop();
            }, 2000);
            
        } catch (error) {
            console.error('Ошибка начала игры:', error);
            alert('Не удалось начать игру. Попробуйте еще раз.');
            this.showScreen('main-menu');
        }
    }
    
    async sendAction(action) {
        if (!this.isPlaying || !this.isAlive || !this.gameId) return;
        
        try {
            const response = await fetch('/api/game/action', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    action: action,
                    player_id: this.playerId
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.isAlive = data.alive;
                this.currentScore = data.distance;
                
                // Обновляем счетчик дистанции
                document.getElementById('distance-counter').textContent = this.currentScore;
                
                // Проверяем новый рекорд
                if (data.best_score > this.bestScore) {
                    this.bestScore = data.best_score;
                    this.saveBestScore();
                    document.getElementById('best-score').textContent = this.bestScore;
                    document.getElementById('current-best').textContent = this.bestScore;
                }
                
                // Если игрок погиб
                if (!this.isAlive) {
                    this.gameOver();
                }
            }
        } catch (error) {
            console.error('Ошибка отправки действия:', error);
        }
    }
    
    async startGameLoop() {
        // Останавливаем предыдущий цикл, если был
        if (this.gameLoopInterval) {
            clearInterval(this.gameLoopInterval);
        }
        
        // Игровой цикл
        this.gameLoopInterval = setInterval(async () => {
            if (!this.isPlaying || !this.isAlive) return;
            
            try {
                // Получаем состояние игры
                const response = await fetch(`/api/game/state/${this.gameId}`);
                const data = await response.json();
                
                this.gameState = data.state;
                
                // Обновляем отображение
                this.updateGameDisplay();
                
                // Автоматическое движение вперед
                if (this.isAlive) {
                    await this.sendAction('gas');
                }
                
            } catch (error) {
                console.error('Ошибка игрового цикла:', error);
            }
        }, 100); // 10 FPS для экономии трафика
        
        // Цикл рендеринга
        this.startRenderLoop();
    }
    
    async startRenderLoop() {
        if (this.renderInterval) {
            clearInterval(this.renderInterval);
        }
        
        this.renderInterval = setInterval(async () => {
            if (!this.isPlaying || !this.gameId) return;
            
            try {
                const response = await fetch(`/api/game/render/${this.gameId}`);
                const blob = await response.blob();
                const img = await createImageBitmap(blob);
                
                this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
                this.ctx.drawImage(img, 0, 0);
                
            } catch (error) {
                console.error('Ошибка рендеринга:', error);
            }
        }, 100); // 10 FPS для рендеринга
    }
    
    updateGameDisplay() {
        if (!this.gameState) return;
        
        // Обновляем счетчики
        const player = this.gameState.player;
        this.currentScore = Math.floor(player.distance / 5);
        
        document.getElementById('distance-counter').textContent = this.currentScore;
        document.getElementById('boost-counter').textContent = player.boost_charges;
        this.boostCharges = player.boost_charges;
        
        // Обновляем состояние жизни
        this.isAlive = player.alive;
    }
    
    updateBoostDisplay() {
        document.getElementById('boost-count').textContent = this.boostCharges;
        document.getElementById('boost-counter').textContent = this.boostCharges;
    }
    
    gameOver() {
        this.isPlaying = false;
        this.isAlive = false;
        
        // Останавливаем игровые циклы
        if (this.gameLoopInterval) {
            clearInterval(this.gameLoopInterval);
            this.gameLoopInterval = null;
        }
        
        if (this.renderInterval) {
            clearInterval(this.renderInterval);
            this.renderInterval = null;
        }
        
        // Обновляем статистику на экране смерти
        document.getElementById('death-distance').textContent = this.currentScore;
        
        const isNewRecord = this.currentScore > this.bestScore;
        document.getElementById('death-new-record').textContent = isNewRecord ? 'ДА!' : 'НЕТ';
        document.getElementById('death-new-record').style.color = isNewRecord ? '#00b894' : '#ff4757';
        
        // Обновляем лучший счет
        if (isNewRecord) {
            this.bestScore = this.currentScore;
            this.saveBestScore();
            document.getElementById('best-score').textContent = this.bestScore;
        }
        
        // Показываем экран смерти
        setTimeout(() => {
            this.showScreen('death-screen');
        }, 1500);
    }
    
    togglePause() {
        if (!this.isPlaying) return;
        
        const pauseScreen = document.getElementById('pause-screen');
        
        if (pauseScreen.classList.contains('active')) {
            // Возобновляем игру
            pauseScreen.classList.remove('active');
            this.startGameLoop();
        } else {
            // Ставим на паузу
            pauseScreen.classList.add('active');
            
            // Обновляем статистику на экране паузы
            document.getElementById('pause-distance').textContent = this.currentScore;
            document.getElementById('pause-best').textContent = this.bestScore;
            
            // Останавливаем игровые циклы
            if (this.gameLoopInterval) {
                clearInterval(this.gameLoopInterval);
                this.gameLoopInterval = null;
            }
            
            if (this.renderInterval) {
                clearInterval(this.renderInterval);
                this.renderInterval = null;
            }
        }
    }
    
    restartGame() {
        // Останавливаем все циклы
        if (this.gameLoopInterval) {
            clearInterval(this.gameLoopInterval);
            this.gameLoopInterval = null;
        }
        
        if (this.renderInterval) {
            clearInterval(this.renderInterval);
            this.renderInterval = null;
        }
        
        // Закрываем все экраны
        document.querySelectorAll('.screen').forEach(screen => {
            screen.classList.remove('active');
        });
        
        // Начинаем новую игру
        setTimeout(() => {
            this.startNewGame();
        }, 500);
    }
    
    returnToMenu() {
        // Останавливаем все циклы
        if (this.gameLoopInterval) {
            clearInterval(this.gameLoopInterval);
            this.gameLoopInterval = null;
        }
        
        if (this.renderInterval) {
            clearInterval(this.renderInterval);
            this.renderInterval = null;
        }
        
        // Сбрасываем состояние игры
        this.isPlaying = false;
        this.isAlive = true;
        this.gameId = null;
        this.gameState = null;
        
        // Очищаем canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Показываем главное меню
        this.showScreen('main-menu');
    }
    
    showScreen(screenId) {
        // Скрываем все экраны
        document.querySelectorAll('.screen').forEach(screen => {
            screen.classList.remove('active');
        });
        
        // Показываем нужный экран
        document.getElementById(screenId).classList.add('active');
        
        // Обновляем отображение лучшего счета
        document.getElementById('best-score').textContent = this.bestScore;
    }
    
    showAbout() {
        if (window.Telegram && Telegram.WebApp) {
            Telegram.WebApp.showAlert(
                'Trash Kart Racer\n\n' +
                'Андеграундные гонки на свалке!\n' +
                'Уворачивайся от голов, выполняй трюки\n' +
                'и ставь новые рекорды!\n\n' +
                'Создано для Telegram Mini Apps'
            );
        } else {
            alert('Trash Kart Racer\n\nАндеграундные гонки на свалке!');
        }
    }
    
    loadBestScore() {
        const savedScore = localStorage.getItem('trash_kart_best_score');
        if (savedScore) {
            this.bestScore = parseInt(savedScore);
            document.getElementById('best-score').textContent = this.bestScore;
        }
    }
    
    saveBestScore() {
        localStorage.setItem('trash_kart_best_score', this.bestScore.toString());
    }
}

// Инициализация игры при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    window.game = new TrashKartGame();
    
    // Предотвращение стандартных жестов на мобильных устройствах
    document.addEventListener('touchmove', (e) => {
        if (e.target.classList.contains('control-btn')) {
            e.preventDefault();
        }
    }, { passive: false });
    
    // Функции для обработки касаний (глобальные для использования в HTML)
    window.onTouchStart = function(e) {
        e.preventDefault();
        if (window.game && e.target.closest('.control-btn')) {
            const btn = e.target.closest('.control-btn');
            if (btn.id === 'btn-brake') {
                window.game.touchControls.brake = true;
                window.game.sendAction('brake');
            } else if (btn.id === 'btn-gas') {
                window.game.touchControls.gas = true;
                window.game.sendAction('gas');
            }
        }
    };
    
    window.onTouchEnd = function(e) {
        e.preventDefault();
        if (window.game) {
            window.game.touchControls.brake = false;
            window.game.touchControls.gas = false;
        }
    };
});
