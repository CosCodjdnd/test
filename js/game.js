/**
 * Main Game Controller for Past Jupiter: Odyssey
 */

class Game {
    constructor() {
        this.renderer = null;
        this.scene = null;
        this.camera = null;
        this.clock = new THREE.Clock();
        this.player = null;
        this.galaxy = null;
        this.ship = null;
        this.weapons = null;
        this.hud = null;
        this.isRunning = false;
        this.selectedRole = null;

        // Fog / ambient
        this.ambientLight = null;
        this.nebulae = [];

        this.init();
    }

    init() {
        // Setup renderer
        this.renderer = new THREE.WebGLRenderer({
            canvas: document.getElementById('gameCanvas'),
            antialias: true,
            alpha: false
        });
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
        this.renderer.toneMappingExposure = 1.0;

        // Scene
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x000005);

        // Camera
        this.camera = new THREE.PerspectiveCamera(
            75, window.innerWidth / window.innerHeight, 0.1, 200000
        );
        this.scene.add(this.camera);

        // Ambient light
        this.ambientLight = new THREE.AmbientLight(0x111122, 0.3);
        this.scene.add(this.ambientLight);

        // Directional light (distant sun simulation)
        const dirLight = new THREE.DirectionalLight(0xffeedd, 0.5);
        dirLight.position.set(1000, 500, -1000);
        this.scene.add(dirLight);

        // HUD
        this.hud = new HUD();

        // Handle resize
        window.addEventListener('resize', () => this.onResize());

        // Setup title screen
        this.setupTitleScreen();

        // Start render loop for title screen background
        this.renderTitleBackground();
    }

    setupTitleScreen() {
        const roleButtons = document.querySelectorAll('.role-btn');
        const startBtn = document.getElementById('start-btn');

        roleButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                roleButtons.forEach(b => b.classList.remove('selected'));
                btn.classList.add('selected');
                this.selectedRole = btn.dataset.role;
                startBtn.disabled = false;
            });
        });

        startBtn.addEventListener('click', () => {
            if (this.selectedRole) {
                this.startGame();
            }
        });
    }

    renderTitleBackground() {
        // Simple animated background for title screen
        const titleAnim = () => {
            if (this.isRunning) return;
            requestAnimationFrame(titleAnim);
            this.renderer.render(this.scene, this.camera);
        };

        // Add some stars for title background
        const starsGeom = new THREE.BufferGeometry();
        const positions = [];
        for (let i = 0; i < 3000; i++) {
            positions.push(
                (Math.random() - 0.5) * 2000,
                (Math.random() - 0.5) * 2000,
                -Math.random() * 2000
            );
        }
        starsGeom.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
        const starsMat = new THREE.PointsMaterial({
            color: 0xffffff,
            size: 1.5,
            transparent: true,
            opacity: 0.7,
            sizeAttenuation: false
        });
        this.titleStars = new THREE.Points(starsGeom, starsMat);
        this.scene.add(this.titleStars);

        titleAnim();
    }

    async startGame() {
        const titleScreen = document.getElementById('title-screen');
        const loadingScreen = document.getElementById('loading-screen');
        const loadingBar = document.getElementById('loading-bar');
        const loadingText = document.getElementById('loading-text');

        // Fade out title
        titleScreen.style.display = 'none';
        loadingScreen.style.display = 'flex';

        // Remove title stars
        if (this.titleStars) {
            this.scene.remove(this.titleStars);
        }

        // Loading phases
        const phases = [
            { text: 'Generating galaxy...', progress: 10 },
            { text: 'Creating star systems...', progress: 30 },
            { text: 'Sculpting planets...', progress: 50 },
            { text: 'Building voxel terrain...', progress: 70 },
            { text: 'Initializing systems...', progress: 85 },
            { text: 'Ready for launch...', progress: 100 }
        ];

        for (const phase of phases) {
            loadingText.textContent = phase.text;
            loadingBar.style.width = phase.progress + '%';
            await this.sleep(300);
        }

        // Generate galaxy
        this.galaxy = new Galaxy(Math.floor(Math.random() * 999999));
        this.galaxy.generate(15);
        this.scene.add(this.galaxy.group);

        // Create nebula effects
        this.createNebulae();

        // Position player near first system's first planet
        const startSystem = this.galaxy.currentSystem;
        const startPlanet = startSystem.planets[0];
        const planetPos = startPlanet.getWorldPosition().add(startSystem.getWorldPosition());
        const startOffset = new THREE.Vector3(0, startPlanet.radius * 3, startPlanet.radius * 2);

        // Create player
        this.player = new Player(this.camera);
        this.player.role = this.selectedRole;
        this.player.position.copy(planetPos).add(startOffset);

        // Create ship
        this.ship = new Ship(this.scene);
        this.player.ship = this.ship;
        this.ship.setOccupied(true);

        // Create weapons
        this.weapons = new Weapons(this.scene, this.camera);

        // Make weapons accessible
        window.game = this;

        await this.sleep(500);

        // Hide loading, show HUD
        loadingScreen.style.display = 'none';
        this.hud.show();
        document.body.style.cursor = 'none';

        // Start game loop
        this.isRunning = true;
        this.clock.start();
        this.gameLoop();
    }

    createNebulae() {
        // Create colorful nebula clouds in the distance
        const nebulaColors = [0x440066, 0x003366, 0x660033, 0x336600, 0x663300];
        const rng = Utils.seededRandom(this.galaxy.seed + 500);

        for (let i = 0; i < 8; i++) {
            const nebulaGeom = new THREE.SphereGeometry(
                3000 + rng() * 5000,
                16, 16
            );
            const nebulaMat = new THREE.MeshBasicMaterial({
                color: nebulaColors[Math.floor(rng() * nebulaColors.length)],
                transparent: true,
                opacity: 0.03 + rng() * 0.04,
                side: THREE.DoubleSide,
                depthWrite: false
            });
            const nebula = new THREE.Mesh(nebulaGeom, nebulaMat);
            nebula.position.set(
                (rng() - 0.5) * 40000,
                (rng() - 0.5) * 10000,
                (rng() - 0.5) * 40000
            );
            this.scene.add(nebula);
            this.nebulae.push(nebula);
        }
    }

    gameLoop() {
        if (!this.isRunning) return;
        requestAnimationFrame(() => this.gameLoop());

        const deltaTime = Math.min(this.clock.getDelta(), 0.05);

        // Update player
        this.player.update(deltaTime, this.galaxy);

        // Update galaxy (planet orbits, LODs)
        this.galaxy.update(deltaTime, this.player.position);

        // Update weapons
        this.weapons.update(deltaTime, this.player.mouseDown && !this.player.isInShip);

        // Update HUD
        this.hud.update(this.player, this.galaxy, this.weapons);

        // Update atmosphere intensity based on proximity
        this.updateAtmosphereEffects();

        // Render
        this.renderer.render(this.scene, this.camera);
    }

    updateAtmosphereEffects() {
        if (this.player.nearPlanet && this.player.altitude < this.player.nearPlanet.radius) {
            const t = 1.0 - (this.player.altitude / this.player.nearPlanet.radius);
            const atmosColor = this.player.nearPlanet.colors.atmosphere;

            // Gradually add fog as we enter atmosphere
            this.scene.fog = new THREE.FogExp2(
                atmosColor,
                Utils.lerp(0, 0.001, Utils.smoothstep(0, 1, t))
            );

            // Increase ambient light on planet surface
            this.ambientLight.intensity = Utils.lerp(0.3, 0.8, t);
        } else {
            this.scene.fog = null;
            this.ambientLight.intensity = 0.3;
        }
    }

    onResize() {
        this.camera.aspect = window.innerWidth / window.innerHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(window.innerWidth, window.innerHeight);
    }

    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Start the game when the page loads
window.addEventListener('DOMContentLoaded', () => {
    new Game();
});
