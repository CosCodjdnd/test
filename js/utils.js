/**
 * Utility functions for Past Jupiter: Odyssey
 */
const Utils = {
    /**
     * Seeded random number generator
     */
    seededRandom: function(seed) {
        let s = seed;
        return function() {
            s = (s * 16807 + 0) % 2147483647;
            return (s - 1) / 2147483646;
        };
    },

    /**
     * Linear interpolation
     */
    lerp: function(a, b, t) {
        return a + (b - a) * t;
    },

    /**
     * Clamp a value between min and max
     */
    clamp: function(val, min, max) {
        return Math.max(min, Math.min(max, val));
    },

    /**
     * Map value from one range to another
     */
    map: function(val, inMin, inMax, outMin, outMax) {
        return outMin + (outMax - outMin) * ((val - inMin) / (inMax - inMin));
    },

    /**
     * Generate a random color based on seed
     */
    randomColor: function(seed) {
        const rng = this.seededRandom(seed);
        const h = rng() * 360;
        const s = 40 + rng() * 60;
        const l = 30 + rng() * 40;
        return new THREE.Color().setHSL(h / 360, s / 100, l / 100);
    },

    /**
     * Generate star name
     */
    generateStarName: function(seed) {
        const rng = this.seededRandom(seed);
        const prefixes = ['Alpha', 'Beta', 'Gamma', 'Delta', 'Epsilon', 'Zeta', 'Eta', 'Theta', 'Iota', 'Kappa',
            'Nova', 'Proxima', 'Kepler', 'Gliese', 'Tau', 'Sigma', 'Omega', 'Phi', 'Lambda', 'Mu'];
        const suffixes = ['Centauri', 'Cygni', 'Draconis', 'Eridani', 'Orionis', 'Pegasi', 'Tauri', 'Vega',
            'Hydrae', 'Lyrae', 'Aquarii', 'Bootis', 'Carinae', 'Fornacis', 'Gruis'];
        const prefix = prefixes[Math.floor(rng() * prefixes.length)];
        const suffix = suffixes[Math.floor(rng() * suffixes.length)];
        const num = Math.floor(rng() * 999) + 1;
        return `${prefix} ${suffix}-${num}`;
    },

    /**
     * Generate planet name
     */
    generatePlanetName: function(seed) {
        const rng = this.seededRandom(seed);
        const syllables = ['ar', 'en', 'is', 'ol', 'un', 'ra', 'ke', 'li', 'mo', 'nu',
            'pa', 'te', 'vo', 'za', 'xi', 'by', 'co', 'de', 'fi', 'gu',
            'ha', 'jo', 'ka', 'le', 'mi', 'no', 'pe', 'ri', 'sa', 'tu'];
        const len = 2 + Math.floor(rng() * 3);
        let name = '';
        for (let i = 0; i < len; i++) {
            name += syllables[Math.floor(rng() * syllables.length)];
        }
        return name.charAt(0).toUpperCase() + name.slice(1);
    },

    /**
     * Distance between two Vector3
     */
    distance: function(a, b) {
        return a.distanceTo(b);
    },

    /**
     * Create gradient texture
     */
    createGradientTexture: function(color1, color2) {
        const canvas = document.createElement('canvas');
        canvas.width = 256;
        canvas.height = 256;
        const ctx = canvas.getContext('2d');
        const gradient = ctx.createRadialGradient(128, 128, 0, 128, 128, 128);
        gradient.addColorStop(0, color1);
        gradient.addColorStop(1, color2);
        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, 256, 256);
        return new THREE.CanvasTexture(canvas);
    },

    /**
     * Smooth step
     */
    smoothstep: function(edge0, edge1, x) {
        const t = this.clamp((x - edge0) / (edge1 - edge0), 0.0, 1.0);
        return t * t * (3.0 - 2.0 * t);
    }
};
