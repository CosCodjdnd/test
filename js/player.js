/**
 * Player Controller for Past Jupiter: Odyssey
 * Handles both on-foot and ship controls with seamless transitions
 */

class Player {
    constructor(camera) {
        this.camera = camera;
        this.position = new THREE.Vector3(0, 0, 0);
        this.velocity = new THREE.Vector3(0, 0, 0);
        this.rotation = new THREE.Euler(0, 0, 0, 'YXZ');

        // State
        this.isInShip = true;
        this.isOnPlanet = false;
        this.health = 100;
        this.maxHealth = 100;
        this.role = 'explorer';

        // Movement settings
        this.shipSpeed = 0;
        this.shipMaxSpeed = 500;
        this.shipBoostSpeed = 2000;
        this.shipAcceleration = 200;
        this.shipDeceleration = 100;
        this.footSpeed = 30;
        this.footSprintSpeed = 60;
        this.jumpForce = 15;
        this.gravity = 20;
        this.verticalVelocity = 0;
        this.isGrounded = false;

        // Mouse sensitivity
        this.mouseSensitivity = 0.002;

        // Input state
        this.keys = {};
        this.mouseDown = false;
        this.isBoosting = false;

        // Near planet
        this.nearPlanet = null;
        this.planetDistance = Infinity;
        this.altitude = 0;

        // Ship reference
        this.ship = null;

        this.setupControls();
    }

    setupControls() {
        document.addEventListener('keydown', (e) => {
            this.keys[e.code] = true;
            if (e.code === 'KeyE') this.toggleShip();
            if (e.code === 'Digit1') this.switchWeapon(0);
            if (e.code === 'Digit2') this.switchWeapon(1);
        });

        document.addEventListener('keyup', (e) => {
            this.keys[e.code] = false;
        });

        document.addEventListener('mousedown', (e) => {
            if (e.button === 0) this.mouseDown = true;
        });

        document.addEventListener('mouseup', (e) => {
            if (e.button === 0) this.mouseDown = false;
        });

        document.addEventListener('mousemove', (e) => {
            if (document.pointerLockElement) {
                this.rotation.y -= e.movementX * this.mouseSensitivity;
                this.rotation.x -= e.movementY * this.mouseSensitivity;
                this.rotation.x = Utils.clamp(this.rotation.x, -Math.PI / 2 + 0.01, Math.PI / 2 - 0.01);
            }
        });

        document.addEventListener('click', () => {
            if (!document.pointerLockElement) {
                document.body.requestPointerLock();
            }
        });
    }

    switchWeapon(index) {
        if (window.game && window.game.weapons) {
            window.game.weapons.switchTo(index);
        }
    }

    toggleShip() {
        if (this.isInShip) {
            // Exit ship only if near a planet surface or slow enough
            if (this.isOnPlanet || this.shipSpeed < 10) {
                this.isInShip = false;
                if (this.ship) this.ship.setOccupied(false);
            }
        } else {
            // Enter ship if close enough
            if (this.ship) {
                const shipDist = this.position.distanceTo(this.ship.getPosition());
                if (shipDist < 20) {
                    this.isInShip = true;
                    this.ship.setOccupied(true);
                    this.verticalVelocity = 0;
                }
            }
        }
    }

    update(deltaTime, galaxy) {
        if (this.isInShip) {
            this.updateShipMovement(deltaTime);
        } else {
            this.updateFootMovement(deltaTime);
        }

        // Apply rotation to camera
        this.camera.rotation.copy(this.rotation);
        this.camera.position.copy(this.position);

        // Update near-planet info
        if (galaxy) {
            this.updatePlanetProximity(galaxy);
        }

        // Update ship position
        if (this.ship) {
            if (this.isInShip) {
                this.ship.setPosition(this.position);
                this.ship.setRotation(this.rotation);
            }
            this.ship.update(deltaTime);
        }
    }

    updateShipMovement(deltaTime) {
        const forward = new THREE.Vector3(0, 0, -1);
        const right = new THREE.Vector3(1, 0, 0);
        const up = new THREE.Vector3(0, 1, 0);

        forward.applyEuler(this.rotation);
        right.applyEuler(this.rotation);

        this.isBoosting = this.keys['ShiftLeft'] || this.keys['ShiftRight'];
        const maxSpeed = this.isBoosting ? this.shipBoostSpeed : this.shipMaxSpeed;

        // Acceleration
        if (this.keys['KeyW']) {
            this.shipSpeed = Math.min(this.shipSpeed + this.shipAcceleration * deltaTime, maxSpeed);
        } else if (this.keys['KeyS']) {
            this.shipSpeed = Math.max(this.shipSpeed - this.shipAcceleration * deltaTime, -maxSpeed * 0.3);
        } else {
            // Decelerate
            if (this.shipSpeed > 0) {
                this.shipSpeed = Math.max(0, this.shipSpeed - this.shipDeceleration * deltaTime);
            } else if (this.shipSpeed < 0) {
                this.shipSpeed = Math.min(0, this.shipSpeed + this.shipDeceleration * deltaTime);
            }
        }

        // Strafe
        if (this.keys['KeyA']) {
            this.velocity.add(right.clone().multiplyScalar(-100 * deltaTime));
        }
        if (this.keys['KeyD']) {
            this.velocity.add(right.clone().multiplyScalar(100 * deltaTime));
        }

        // Vertical
        if (this.keys['Space']) {
            this.velocity.add(up.clone().multiplyScalar(100 * deltaTime));
        }
        if (this.keys['KeyC']) {
            this.velocity.add(up.clone().multiplyScalar(-100 * deltaTime));
        }

        // Apply forward velocity
        this.velocity.add(forward.clone().multiplyScalar(this.shipSpeed * deltaTime));

        // Dampen strafe/vertical velocity
        this.velocity.multiplyScalar(0.95);

        // Apply gravity near planets
        if (this.nearPlanet && this.isOnPlanet) {
            const toPlanetCenter = this.nearPlanet.getWorldPosition().sub(this.position).normalize();
            const gravitationalPull = 30 * deltaTime;
            this.velocity.add(toPlanetCenter.multiplyScalar(gravitationalPull));
        }

        this.position.add(this.velocity.clone().multiplyScalar(deltaTime));
    }

    updateFootMovement(deltaTime) {
        const forward = new THREE.Vector3(0, 0, -1);
        const right = new THREE.Vector3(1, 0, 0);

        // Only rotate on Y axis for foot movement direction
        const yaw = new THREE.Euler(0, this.rotation.y, 0);
        forward.applyEuler(yaw);
        right.applyEuler(yaw);

        const speed = (this.keys['ShiftLeft'] || this.keys['ShiftRight']) ? this.footSprintSpeed : this.footSpeed;

        const moveDir = new THREE.Vector3();
        if (this.keys['KeyW']) moveDir.add(forward);
        if (this.keys['KeyS']) moveDir.sub(forward);
        if (this.keys['KeyA']) moveDir.sub(right);
        if (this.keys['KeyD']) moveDir.add(right);

        if (moveDir.lengthSq() > 0) {
            moveDir.normalize().multiplyScalar(speed * deltaTime);
        }

        // Jump
        if (this.keys['Space'] && this.isGrounded) {
            this.verticalVelocity = this.jumpForce;
            this.isGrounded = false;
        }

        // Apply gravity
        if (this.nearPlanet) {
            const planetPos = this.nearPlanet.getWorldPosition();
            const toPlanet = planetPos.clone().sub(this.position);
            const gravDir = toPlanet.normalize();

            this.verticalVelocity -= this.gravity * deltaTime;

            // Move along surface
            // Project moveDir onto surface plane
            const surfaceNormal = gravDir.clone().negate();
            const projectedMove = moveDir.clone().sub(surfaceNormal.clone().multiplyScalar(moveDir.dot(surfaceNormal)));
            this.position.add(projectedMove);

            // Apply vertical velocity along gravity direction
            this.position.add(gravDir.clone().multiplyScalar(this.verticalVelocity * deltaTime));

            // Ground check
            const distFromCenter = this.position.distanceTo(planetPos);
            const dirFromCenter = this.position.clone().sub(planetPos).normalize();
            const surfaceHeight = this.nearPlanet.getSurfaceHeight(dirFromCenter);
            const playerHeight = 5;

            if (distFromCenter <= surfaceHeight + playerHeight) {
                this.position.copy(planetPos).add(dirFromCenter.multiplyScalar(surfaceHeight + playerHeight));
                this.verticalVelocity = 0;
                this.isGrounded = true;
            }
        } else {
            // Floating in space without a planet
            this.position.add(moveDir);
        }
    }

    updatePlanetProximity(galaxy) {
        const nearest = galaxy.findNearestPlanet(this.position);
        if (nearest && nearest.planet) {
            this.nearPlanet = nearest.planet;
            this.planetDistance = nearest.distance;

            const surfaceHeight = this.nearPlanet.radius;
            this.altitude = nearest.distance - surfaceHeight;
            this.isOnPlanet = this.altitude < surfaceHeight * 0.5;
        } else {
            this.nearPlanet = null;
            this.planetDistance = Infinity;
            this.altitude = Infinity;
            this.isOnPlanet = false;
        }
    }

    takeDamage(amount) {
        this.health = Math.max(0, this.health - amount);
        if (this.health <= 0) {
            this.die();
        }
    }

    heal(amount) {
        this.health = Math.min(this.maxHealth, this.health + amount);
    }

    die() {
        // Respawn
        this.health = this.maxHealth;
        this.velocity.set(0, 0, 0);
        this.shipSpeed = 0;
    }

    getCurrentSpeed() {
        if (this.isInShip) {
            return Math.abs(this.shipSpeed);
        }
        return this.velocity.length();
    }
}
