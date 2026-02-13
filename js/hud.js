/**
 * HUD Manager for Past Jupiter: Odyssey
 */

class HUD {
    constructor() {
        this.elements = {
            hud: document.getElementById('hud'),
            speedValue: document.getElementById('speed-value'),
            speedUnit: document.getElementById('speed-unit'),
            altValue: document.getElementById('alt-value'),
            altUnit: document.getElementById('alt-unit'),
            weaponName: document.getElementById('weapon-name'),
            ammoCount: document.getElementById('ammo-count'),
            healthBar: document.getElementById('health-bar'),
            healthText: document.getElementById('health-text'),
            locationInfo: document.getElementById('location-info'),
            planetInfo: document.getElementById('planet-info'),
            crosshair: document.getElementById('crosshair')
        };
    }

    show() {
        this.elements.hud.style.display = 'block';
    }

    hide() {
        this.elements.hud.style.display = 'none';
    }

    update(player, galaxy, weapons) {
        // Speed
        const speed = player.getCurrentSpeed();
        if (speed > 1000) {
            this.elements.speedValue.textContent = (speed / 1000).toFixed(1);
            this.elements.speedUnit.textContent = 'km/s';
        } else {
            this.elements.speedValue.textContent = Math.floor(speed);
            this.elements.speedUnit.textContent = 'm/s';
        }

        // Altitude
        if (player.altitude < Infinity) {
            const alt = player.altitude;
            if (alt > 1000) {
                this.elements.altValue.textContent = (alt / 1000).toFixed(1);
                this.elements.altUnit.textContent = 'Mm';
            } else {
                this.elements.altValue.textContent = Math.floor(alt);
                this.elements.altUnit.textContent = 'km';
            }
        } else {
            this.elements.altValue.textContent = '---';
            this.elements.altUnit.textContent = '';
        }

        // Weapon
        if (weapons) {
            const weapon = weapons.getCurrentWeapon();
            this.elements.weaponName.textContent = weapon.name;
            this.elements.ammoCount.textContent = weapon.ammo === Infinity ? '∞' : weapon.ammo;
        }

        // Health
        this.elements.healthBar.style.width = (player.health / player.maxHealth * 100) + '%';
        this.elements.healthText.textContent = Math.ceil(player.health);

        // Location info
        if (galaxy && galaxy.currentSystem) {
            this.elements.locationInfo.textContent = `System: ${galaxy.currentSystem.name}`;
        }

        if (player.nearPlanet) {
            this.elements.planetInfo.textContent = `Nearest: ${player.nearPlanet.name} [${player.nearPlanet.type.replace('_', ' ').toUpperCase()}]`;
        } else {
            this.elements.planetInfo.textContent = 'Deep Space';
        }

        // Crosshair style based on context
        if (player.isInShip) {
            this.elements.crosshair.textContent = '◇';
            this.elements.crosshair.style.fontSize = '28px';
        } else {
            this.elements.crosshair.textContent = '+';
            this.elements.crosshair.style.fontSize = '24px';
        }
    }
}
