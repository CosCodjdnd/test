/**
 * Galaxy & Star System Generator for Past Jupiter: Odyssey
 */

class StarSystem {
    constructor(seed, position) {
        this.seed = seed;
        this.position = position;
        this.rng = Utils.seededRandom(seed);
        this.name = Utils.generateStarName(seed);
        this.starColor = this.generateStarColor();
        this.starSize = 50 + this.rng() * 150;
        this.planets = [];
        this.group = new THREE.Group();
        this.group.position.copy(position);
        this.star = null;
        this.starLight = null;
        this.isGenerated = false;
    }

    generateStarColor() {
        const types = [
            { color: new THREE.Color(0xffffdd), temp: 'G' },  // Yellow
            { color: new THREE.Color(0xffddaa), temp: 'K' },  // Orange
            { color: new THREE.Color(0xffaaaa), temp: 'M' },  // Red
            { color: new THREE.Color(0xddddff), temp: 'A' },  // White-blue
            { color: new THREE.Color(0xaaaaff), temp: 'B' },  // Blue
            { color: new THREE.Color(0xffffff), temp: 'F' },  // White
        ];
        return types[Math.floor(this.rng() * types.length)];
    }

    generate() {
        if (this.isGenerated) return;

        // Create star
        this.createStar();

        // Generate planets (2-7 per system)
        const planetCount = 2 + Math.floor(this.rng() * 6);
        for (let i = 0; i < planetCount; i++) {
            this.createPlanet(i, planetCount);
        }

        this.isGenerated = true;
    }

    createStar() {
        // Star glow
        const starGeom = new THREE.SphereGeometry(this.starSize, 32, 32);
        const starMat = new THREE.MeshBasicMaterial({
            color: this.starColor.color,
            transparent: true,
            opacity: 1.0
        });
        this.star = new THREE.Mesh(starGeom, starMat);
        this.group.add(this.star);

        // Star corona/glow effect
        const glowGeom = new THREE.SphereGeometry(this.starSize * 1.5, 32, 32);
        const glowMat = new THREE.ShaderMaterial({
            vertexShader: `
                varying vec3 vNormal;
                void main() {
                    vNormal = normalize(normalMatrix * normal);
                    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
                }
            `,
            fragmentShader: `
                uniform vec3 glowColor;
                varying vec3 vNormal;
                void main() {
                    float intensity = pow(0.7 - dot(vNormal, vec3(0.0, 0.0, 1.0)), 2.0);
                    gl_FragColor = vec4(glowColor, intensity * 0.5);
                }
            `,
            uniforms: {
                glowColor: { value: this.starColor.color }
            },
            side: THREE.FrontSide,
            blending: THREE.AdditiveBlending,
            transparent: true,
            depthWrite: false
        });
        const glow = new THREE.Mesh(glowGeom, glowMat);
        this.group.add(glow);

        // Point light from star
        this.starLight = new THREE.PointLight(this.starColor.color, 2, this.starSize * 100);
        this.starLight.castShadow = true;
        this.group.add(this.starLight);
    }

    createPlanet(index, total) {
        const orbitRadius = (this.starSize * 3) + (index + 1) * (400 + this.rng() * 300);
        const angle = this.rng() * Math.PI * 2;
        const planetSeed = this.seed * 1000 + index * 137;
        const planetRadius = 80 + this.rng() * 250;

        const planetPos = new THREE.Vector3(
            Math.cos(angle) * orbitRadius,
            (this.rng() - 0.5) * 100,
            Math.sin(angle) * orbitRadius
        );

        const planet = new VoxelPlanet({
            seed: planetSeed,
            position: planetPos,
            radius: planetRadius
        });

        planet.orbitRadius = orbitRadius;
        planet.orbitAngle = angle;
        planet.orbitSpeed = 0.01 / (index + 1);

        this.planets.push(planet);
    }

    generatePlanetMeshes() {
        for (const planet of this.planets) {
            if (!planet.isGenerated) {
                planet.generate();
                this.group.add(planet.group);
            }
        }
    }

    update(deltaTime) {
        // Rotate star
        if (this.star) {
            this.star.rotation.y += deltaTime * 0.05;
        }

        // Orbit planets
        for (const planet of this.planets) {
            planet.orbitAngle += planet.orbitSpeed * deltaTime;
            planet.group.position.x = Math.cos(planet.orbitAngle) * planet.orbitRadius;
            planet.group.position.z = Math.sin(planet.orbitAngle) * planet.orbitRadius;
            planet.update(deltaTime);
        }
    }

    getWorldPosition() {
        return this.group.position.clone();
    }
}

class Galaxy {
    constructor(seed) {
        this.seed = seed || Math.floor(Math.random() * 999999);
        this.rng = Utils.seededRandom(this.seed);
        this.systems = [];
        this.group = new THREE.Group();
        this.starfield = null;
        this.currentSystem = null;
    }

    generate(systemCount) {
        systemCount = systemCount || 20;

        // Create background starfield
        this.createStarfield();

        // Generate star systems in a spiral pattern
        for (let i = 0; i < systemCount; i++) {
            const angle = (i / systemCount) * Math.PI * 4 + this.rng() * 0.5;
            const armOffset = this.rng() * 2000;
            const radius = 3000 + i * 500 + armOffset;

            const pos = new THREE.Vector3(
                Math.cos(angle) * radius + (this.rng() - 0.5) * 1500,
                (this.rng() - 0.5) * 800,
                Math.sin(angle) * radius + (this.rng() - 0.5) * 1500
            );

            const systemSeed = this.seed * 100 + i * 31;
            const system = new StarSystem(systemSeed, pos);
            system.generate();
            this.systems.push(system);
            this.group.add(system.group);
        }

        // Generate the closest system's planets in detail
        if (this.systems.length > 0) {
            this.currentSystem = this.systems[0];
            this.currentSystem.generatePlanetMeshes();
        }
    }

    createStarfield() {
        const starsGeom = new THREE.BufferGeometry();
        const starPositions = [];
        const starColors = [];
        const starSizes = [];

        for (let i = 0; i < 15000; i++) {
            const r = 20000 + this.rng() * 80000;
            const theta = this.rng() * Math.PI * 2;
            const phi = Math.acos(2 * this.rng() - 1);

            starPositions.push(
                r * Math.sin(phi) * Math.cos(theta),
                r * Math.sin(phi) * Math.sin(theta),
                r * Math.cos(phi)
            );

            const brightness = 0.5 + this.rng() * 0.5;
            const tint = this.rng();
            if (tint < 0.3) {
                starColors.push(brightness, brightness * 0.9, brightness * 0.8);
            } else if (tint < 0.5) {
                starColors.push(brightness * 0.8, brightness * 0.85, brightness);
            } else {
                starColors.push(brightness, brightness, brightness);
            }

            starSizes.push(0.5 + this.rng() * 2.0);
        }

        starsGeom.setAttribute('position', new THREE.Float32BufferAttribute(starPositions, 3));
        starsGeom.setAttribute('color', new THREE.Float32BufferAttribute(starColors, 3));
        starsGeom.setAttribute('size', new THREE.Float32BufferAttribute(starSizes, 1));

        const starsMat = new THREE.PointsMaterial({
            size: 3,
            vertexColors: true,
            transparent: true,
            opacity: 0.8,
            sizeAttenuation: false
        });

        this.starfield = new THREE.Points(starsGeom, starsMat);
        this.group.add(this.starfield);
    }

    findNearestSystem(position) {
        let nearest = null;
        let nearestDist = Infinity;

        for (const system of this.systems) {
            const dist = position.distanceTo(system.getWorldPosition());
            if (dist < nearestDist) {
                nearestDist = dist;
                nearest = system;
            }
        }

        return { system: nearest, distance: nearestDist };
    }

    findNearestPlanet(position) {
        if (!this.currentSystem) return null;

        let nearest = null;
        let nearestDist = Infinity;

        for (const planet of this.currentSystem.planets) {
            const planetWorldPos = planet.getWorldPosition().add(this.currentSystem.getWorldPosition());
            const dist = position.distanceTo(planetWorldPos);
            if (dist < nearestDist) {
                nearestDist = dist;
                nearest = planet;
            }
        }

        return { planet: nearest, distance: nearestDist };
    }

    update(deltaTime, playerPosition) {
        // Update current system
        if (this.currentSystem) {
            this.currentSystem.update(deltaTime);

            // Update planet LODs based on distance
            for (const planet of this.currentSystem.planets) {
                const planetWorldPos = planet.getWorldPosition().add(this.currentSystem.getWorldPosition());
                const dist = playerPosition.distanceTo(planetWorldPos);
                planet.updateLOD(dist);
            }
        }

        // Check if we need to switch to a different system
        const nearest = this.findNearestSystem(playerPosition);
        if (nearest.system && nearest.system !== this.currentSystem) {
            if (nearest.distance < 5000) {
                this.currentSystem = nearest.system;
                this.currentSystem.generatePlanetMeshes();
            }
        }
    }
}
