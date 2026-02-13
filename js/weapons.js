/**
 * Weapons System for Past Jupiter: Odyssey
 * Gun and Pistol with projectile physics
 */

class Weapons {
    constructor(scene, camera) {
        this.scene = scene;
        this.camera = camera;
        this.currentWeapon = 0;
        this.weapons = [
            {
                name: 'PISTOL',
                damage: 15,
                fireRate: 0.3,
                projectileSpeed: 300,
                projectileColor: 0x00ffcc,
                projectileSize: 0.15,
                spread: 0.02,
                ammo: Infinity,
                maxAmmo: Infinity
            },
            {
                name: 'RIFLE',
                damage: 35,
                fireRate: 0.15,
                projectileSpeed: 500,
                projectileColor: 0xff4400,
                projectileSize: 0.2,
                spread: 0.01,
                ammo: Infinity,
                maxAmmo: Infinity
            }
        ];

        this.lastFireTime = 0;
        this.projectiles = [];
        this.muzzleFlash = null;
        this.weaponModel = null;

        this.createWeaponModels();
        this.createMuzzleFlash();
    }

    createWeaponModels() {
        this.weaponGroup = new THREE.Group();

        // Pistol model
        const pistolGroup = new THREE.Group();
        const pistolBody = new THREE.Mesh(
            new THREE.BoxGeometry(0.15, 0.15, 0.5),
            new THREE.MeshPhongMaterial({ color: 0x333344, flatShading: true })
        );
        pistolGroup.add(pistolBody);

        const pistolGrip = new THREE.Mesh(
            new THREE.BoxGeometry(0.1, 0.25, 0.12),
            new THREE.MeshPhongMaterial({ color: 0x222233, flatShading: true })
        );
        pistolGrip.position.set(0, -0.15, 0.1);
        pistolGrip.rotation.x = 0.2;
        pistolGroup.add(pistolGrip);

        const pistolBarrel = new THREE.Mesh(
            new THREE.BoxGeometry(0.08, 0.08, 0.2),
            new THREE.MeshPhongMaterial({ color: 0x444455, flatShading: true })
        );
        pistolBarrel.position.set(0, 0.02, -0.3);
        pistolGroup.add(pistolBarrel);

        pistolGroup.position.set(0.3, -0.25, -0.5);
        this.pistolModel = pistolGroup;

        // Rifle model
        const rifleGroup = new THREE.Group();
        const rifleBody = new THREE.Mesh(
            new THREE.BoxGeometry(0.12, 0.18, 0.9),
            new THREE.MeshPhongMaterial({ color: 0x334455, flatShading: true })
        );
        rifleGroup.add(rifleBody);

        const rifleStock = new THREE.Mesh(
            new THREE.BoxGeometry(0.1, 0.15, 0.3),
            new THREE.MeshPhongMaterial({ color: 0x553322, flatShading: true })
        );
        rifleStock.position.set(0, -0.02, 0.5);
        rifleGroup.add(rifleStock);

        const rifleBarrel = new THREE.Mesh(
            new THREE.BoxGeometry(0.06, 0.06, 0.4),
            new THREE.MeshPhongMaterial({ color: 0x445566, flatShading: true })
        );
        rifleBarrel.position.set(0, 0.03, -0.6);
        rifleGroup.add(rifleBarrel);

        const rifleSight = new THREE.Mesh(
            new THREE.BoxGeometry(0.04, 0.06, 0.15),
            new THREE.MeshPhongMaterial({ color: 0x556677, flatShading: true })
        );
        rifleSight.position.set(0, 0.12, -0.1);
        rifleGroup.add(rifleSight);

        const rifleGrip = new THREE.Mesh(
            new THREE.BoxGeometry(0.08, 0.2, 0.1),
            new THREE.MeshPhongMaterial({ color: 0x222233, flatShading: true })
        );
        rifleGrip.position.set(0, -0.15, 0.15);
        rifleGrip.rotation.x = 0.15;
        rifleGroup.add(rifleGrip);

        rifleGroup.position.set(0.3, -0.3, -0.6);
        this.rifleModel = rifleGroup;

        // Start with pistol
        this.weaponGroup.add(this.pistolModel);
        this.camera.add(this.weaponGroup);
    }

    createMuzzleFlash() {
        const flashGeom = new THREE.SphereGeometry(0.1, 6, 6);
        const flashMat = new THREE.MeshBasicMaterial({
            color: 0xffff00,
            transparent: true,
            opacity: 0
        });
        this.muzzleFlash = new THREE.Mesh(flashGeom, flashMat);
        this.muzzleFlash.position.set(0.3, -0.2, -0.9);
        this.camera.add(this.muzzleFlash);
    }

    switchTo(index) {
        if (index < 0 || index >= this.weapons.length) return;
        this.currentWeapon = index;

        // Update weapon model
        while (this.weaponGroup.children.length > 0) {
            this.weaponGroup.remove(this.weaponGroup.children[0]);
        }

        if (index === 0) {
            this.weaponGroup.add(this.pistolModel);
        } else {
            this.weaponGroup.add(this.rifleModel);
        }
    }

    fire() {
        const now = performance.now() / 1000;
        const weapon = this.weapons[this.currentWeapon];

        if (now - this.lastFireTime < weapon.fireRate) return;
        this.lastFireTime = now;

        // Create projectile
        const direction = new THREE.Vector3(0, 0, -1);
        direction.applyQuaternion(this.camera.quaternion);

        // Add spread
        direction.x += (Math.random() - 0.5) * weapon.spread;
        direction.y += (Math.random() - 0.5) * weapon.spread;
        direction.normalize();

        const projectileGeom = new THREE.SphereGeometry(weapon.projectileSize, 4, 4);
        const projectileMat = new THREE.MeshBasicMaterial({
            color: weapon.projectileColor,
            transparent: true,
            opacity: 0.9
        });
        const projectile = new THREE.Mesh(projectileGeom, projectileMat);
        projectile.position.copy(this.camera.position);

        // Trail
        const trailGeom = new THREE.CylinderGeometry(weapon.projectileSize * 0.3, weapon.projectileSize * 0.3, 2, 4);
        const trailMat = new THREE.MeshBasicMaterial({
            color: weapon.projectileColor,
            transparent: true,
            opacity: 0.4
        });
        const trail = new THREE.Mesh(trailGeom, trailMat);
        trail.rotation.x = Math.PI / 2;
        trail.position.z = 1;
        projectile.add(trail);

        // Light on projectile
        const projectileLight = new THREE.PointLight(weapon.projectileColor, 0.5, 20);
        projectile.add(projectileLight);

        this.scene.add(projectile);
        this.projectiles.push({
            mesh: projectile,
            direction: direction,
            speed: weapon.projectileSpeed,
            damage: weapon.damage,
            lifetime: 3.0,
            age: 0
        });

        // Muzzle flash
        this.muzzleFlash.material.opacity = 1.0;
        this.muzzleFlash.material.color.setHex(weapon.projectileColor);

        // Weapon kick animation
        this.weaponGroup.position.z = 0.1;
    }

    update(deltaTime, isFiring) {
        if (isFiring) {
            this.fire();
        }

        // Update projectiles
        for (let i = this.projectiles.length - 1; i >= 0; i--) {
            const proj = this.projectiles[i];
            proj.age += deltaTime;

            if (proj.age > proj.lifetime) {
                this.scene.remove(proj.mesh);
                this.projectiles.splice(i, 1);
                continue;
            }

            proj.mesh.position.add(
                proj.direction.clone().multiplyScalar(proj.speed * deltaTime)
            );

            // Fade out
            proj.mesh.material.opacity = 1.0 - (proj.age / proj.lifetime);
        }

        // Muzzle flash fade
        if (this.muzzleFlash.material.opacity > 0) {
            this.muzzleFlash.material.opacity -= deltaTime * 15;
        }

        // Weapon recoil recovery
        this.weaponGroup.position.z *= 0.85;

        // Weapon sway
        const time = performance.now() * 0.001;
        this.weaponGroup.position.x = Math.sin(time * 1.5) * 0.003;
        this.weaponGroup.position.y = Math.cos(time * 2) * 0.002;
    }

    getCurrentWeapon() {
        return this.weapons[this.currentWeapon];
    }
}
