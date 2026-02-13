/**
 * Ship class for Past Jupiter: Odyssey
 */

class Ship {
    constructor(scene) {
        this.scene = scene;
        this.group = new THREE.Group();
        this.position = new THREE.Vector3();
        this.rotation = new THREE.Euler();
        this.occupied = true;
        this.engineGlow = null;

        this.createModel();
        scene.add(this.group);
    }

    createModel() {
        // Main hull - sleek fuselage
        const hullGeom = new THREE.Group();

        // Body
        const bodyGeom = new THREE.BoxGeometry(4, 2, 12);
        const bodyMat = new THREE.MeshPhongMaterial({
            color: 0x445566,
            specular: 0x222233,
            shininess: 60,
            flatShading: true
        });
        const body = new THREE.Mesh(bodyGeom, bodyMat);
        hullGeom.add(body);

        // Cockpit
        const cockpitGeom = new THREE.BoxGeometry(2.5, 1.5, 3);
        const cockpitMat = new THREE.MeshPhongMaterial({
            color: 0x88ccff,
            specular: 0xffffff,
            shininess: 100,
            transparent: true,
            opacity: 0.6
        });
        const cockpit = new THREE.Mesh(cockpitGeom, cockpitMat);
        cockpit.position.set(0, 1.2, -2);
        hullGeom.add(cockpit);

        // Wings
        const wingGeom = new THREE.BoxGeometry(12, 0.5, 6);
        const wingMat = new THREE.MeshPhongMaterial({
            color: 0x334455,
            specular: 0x222233,
            shininess: 40,
            flatShading: true
        });
        const wings = new THREE.Mesh(wingGeom, wingMat);
        wings.position.set(0, -0.3, 1);
        hullGeom.add(wings);

        // Wing tips
        const tipGeom = new THREE.BoxGeometry(1, 2, 3);
        const tipMat = new THREE.MeshPhongMaterial({
            color: 0x556677,
            flatShading: true
        });
        const leftTip = new THREE.Mesh(tipGeom, tipMat);
        leftTip.position.set(-6.5, 0.5, 1);
        hullGeom.add(leftTip);

        const rightTip = new THREE.Mesh(tipGeom, tipMat);
        rightTip.position.set(6.5, 0.5, 1);
        hullGeom.add(rightTip);

        // Engine exhaust
        const engineGeom = new THREE.CylinderGeometry(0.8, 1.2, 2, 6);
        const engineMat = new THREE.MeshPhongMaterial({
            color: 0x333344,
            flatShading: true
        });

        const leftEngine = new THREE.Mesh(engineGeom, engineMat);
        leftEngine.rotation.x = Math.PI / 2;
        leftEngine.position.set(-2, -0.3, 6);
        hullGeom.add(leftEngine);

        const rightEngine = new THREE.Mesh(engineGeom, engineMat);
        rightEngine.rotation.x = Math.PI / 2;
        rightEngine.position.set(2, -0.3, 6);
        hullGeom.add(rightEngine);

        // Engine glow
        const glowGeom = new THREE.SphereGeometry(1, 8, 8);
        const glowMat = new THREE.MeshBasicMaterial({
            color: 0x00aaff,
            transparent: true,
            opacity: 0.6
        });

        const leftGlow = new THREE.Mesh(glowGeom, glowMat);
        leftGlow.position.set(-2, -0.3, 7);
        hullGeom.add(leftGlow);

        const rightGlow = new THREE.Mesh(glowGeom, glowMat);
        rightGlow.position.set(2, -0.3, 7);
        hullGeom.add(rightGlow);

        this.engineGlow = [leftGlow, rightGlow];

        // Nose
        const noseGeom = new THREE.BoxGeometry(2, 1.5, 4);
        const noseMat = new THREE.MeshPhongMaterial({
            color: 0x556677,
            flatShading: true
        });
        const nose = new THREE.Mesh(noseGeom, noseMat);
        nose.position.set(0, 0, -6);
        hullGeom.add(nose);

        this.group.add(hullGeom);

        // Add point light for engines
        const engineLight = new THREE.PointLight(0x0088ff, 1, 30);
        engineLight.position.set(0, 0, 7);
        this.group.add(engineLight);
    }

    setPosition(pos) {
        this.position.copy(pos);
        if (!this.occupied) {
            // Ship stays where it was parked
        } else {
            this.group.position.copy(pos);
        }
    }

    setRotation(rot) {
        this.rotation.copy(rot);
        if (this.occupied) {
            this.group.rotation.copy(rot);
        }
    }

    setOccupied(val) {
        this.occupied = val;
        this.group.visible = !val; // Hide when player is inside (first person)
    }

    getPosition() {
        return this.group.position.clone();
    }

    update(deltaTime) {
        // Engine glow pulsing
        if (this.engineGlow) {
            const pulse = 0.4 + Math.sin(Date.now() * 0.005) * 0.2;
            for (const glow of this.engineGlow) {
                glow.material.opacity = this.occupied ? pulse : 0.1;
            }
        }
    }
}
