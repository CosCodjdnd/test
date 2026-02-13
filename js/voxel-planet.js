/**
 * Voxel Planet Generator for Past Jupiter: Odyssey
 * Generates varied planets using simplex noise - water worlds, mountains, plains, etc.
 */

const PLANET_TYPES = {
    WATER_WORLD: 'water_world',
    MOUNTAINOUS: 'mountainous',
    FLAT_PLAINS: 'flat_plains',
    DESERT: 'desert',
    ICE: 'ice',
    VOLCANIC: 'volcanic',
    FOREST: 'forest',
    ALIEN: 'alien'
};

class VoxelPlanet {
    constructor(params) {
        this.seed = params.seed || Math.random() * 99999;
        this.position = params.position || new THREE.Vector3();
        this.radius = params.radius || 200;
        this.type = params.type || this.determinePlanetType();
        this.name = params.name || Utils.generatePlanetName(this.seed);
        this.noise = new SimplexNoise(this.seed);
        this.group = new THREE.Group();
        this.group.position.copy(this.position);
        this.voxelSize = 4;
        this.lodMeshes = {};
        this.atmosphere = null;
        this.isGenerated = false;
        this.colors = this.getPlanetColors();
    }

    determinePlanetType() {
        const rng = Utils.seededRandom(this.seed);
        const types = Object.values(PLANET_TYPES);
        return types[Math.floor(rng() * types.length)];
    }

    getPlanetColors() {
        const rng = Utils.seededRandom(this.seed + 100);
        switch (this.type) {
            case PLANET_TYPES.WATER_WORLD:
                return {
                    primary: new THREE.Color(0x0055aa),
                    secondary: new THREE.Color(0x003366),
                    accent: new THREE.Color(0x00aaff),
                    atmosphere: new THREE.Color(0x4488ff),
                    deep: new THREE.Color(0x001133)
                };
            case PLANET_TYPES.MOUNTAINOUS:
                return {
                    primary: new THREE.Color(0x666655),
                    secondary: new THREE.Color(0x888877),
                    accent: new THREE.Color(0xffffff),
                    atmosphere: new THREE.Color(0x88aacc),
                    deep: new THREE.Color(0x443322)
                };
            case PLANET_TYPES.FLAT_PLAINS:
                return {
                    primary: new THREE.Color(0x44aa44),
                    secondary: new THREE.Color(0x66cc44),
                    accent: new THREE.Color(0x88dd66),
                    atmosphere: new THREE.Color(0x88ccff),
                    deep: new THREE.Color(0x336633)
                };
            case PLANET_TYPES.DESERT:
                return {
                    primary: new THREE.Color(0xcc9944),
                    secondary: new THREE.Color(0xddaa55),
                    accent: new THREE.Color(0xeebb66),
                    atmosphere: new THREE.Color(0xddaa77),
                    deep: new THREE.Color(0x886633)
                };
            case PLANET_TYPES.ICE:
                return {
                    primary: new THREE.Color(0xaaccee),
                    secondary: new THREE.Color(0xccddff),
                    accent: new THREE.Color(0xffffff),
                    atmosphere: new THREE.Color(0xaaddff),
                    deep: new THREE.Color(0x6688aa)
                };
            case PLANET_TYPES.VOLCANIC:
                return {
                    primary: new THREE.Color(0x332211),
                    secondary: new THREE.Color(0x554433),
                    accent: new THREE.Color(0xff4400),
                    atmosphere: new THREE.Color(0xff6633),
                    deep: new THREE.Color(0x221100)
                };
            case PLANET_TYPES.FOREST:
                return {
                    primary: new THREE.Color(0x225522),
                    secondary: new THREE.Color(0x337733),
                    accent: new THREE.Color(0x44aa44),
                    atmosphere: new THREE.Color(0x66cc88),
                    deep: new THREE.Color(0x113311)
                };
            case PLANET_TYPES.ALIEN:
                return {
                    primary: new THREE.Color().setHSL(rng() * 0.3 + 0.7, 0.8, 0.4),
                    secondary: new THREE.Color().setHSL(rng() * 0.3 + 0.7, 0.6, 0.5),
                    accent: new THREE.Color().setHSL(rng() * 0.3 + 0.7, 0.9, 0.6),
                    atmosphere: new THREE.Color().setHSL(rng() * 0.3 + 0.7, 0.5, 0.6),
                    deep: new THREE.Color().setHSL(rng() * 0.3 + 0.7, 0.7, 0.2)
                };
            default:
                return {
                    primary: new THREE.Color(0x666666),
                    secondary: new THREE.Color(0x888888),
                    accent: new THREE.Color(0xaaaaaa),
                    atmosphere: new THREE.Color(0x8888aa),
                    deep: new THREE.Color(0x444444)
                };
        }
    }

    getTerrainHeight(x, y, z) {
        const nx = x / this.radius;
        const ny = y / this.radius;
        const nz = z / this.radius;

        let height = 0;

        switch (this.type) {
            case PLANET_TYPES.WATER_WORLD:
                height = this.noise.fbm(nx * 2, ny * 2, nz * 2, 3, 2.0, 0.5) * 0.1;
                height = Math.min(height, 0.05);
                break;

            case PLANET_TYPES.MOUNTAINOUS:
                height = this.noise.fbm(nx * 3, ny * 3, nz * 3, 6, 2.2, 0.55) * 0.6;
                height = Math.abs(height) * 1.5;
                const ridgeNoise = 1.0 - Math.abs(this.noise.noise3D(nx * 4, ny * 4, nz * 4));
                height += ridgeNoise * 0.3;
                break;

            case PLANET_TYPES.FLAT_PLAINS:
                height = this.noise.fbm(nx * 2, ny * 2, nz * 2, 3, 2.0, 0.4) * 0.08;
                height += this.noise.noise3D(nx * 8, ny * 8, nz * 8) * 0.02;
                break;

            case PLANET_TYPES.DESERT:
                const dunes = Math.abs(this.noise.noise3D(nx * 5, ny * 5, nz * 5));
                height = dunes * 0.2 + this.noise.fbm(nx * 2, ny * 2, nz * 2, 3, 2.0, 0.45) * 0.15;
                break;

            case PLANET_TYPES.ICE:
                height = this.noise.fbm(nx * 3, ny * 3, nz * 3, 4, 2.0, 0.5) * 0.2;
                const cracks = Math.abs(this.noise.noise3D(nx * 10, ny * 10, nz * 10));
                height -= (1.0 - cracks) * 0.05;
                break;

            case PLANET_TYPES.VOLCANIC:
                height = this.noise.fbm(nx * 2, ny * 2, nz * 2, 4, 2.0, 0.5) * 0.3;
                const volcanoes = this.noise.noise3D(nx * 1.5, ny * 1.5, nz * 1.5);
                if (volcanoes > 0.5) {
                    height += (volcanoes - 0.5) * 2.0 * 0.5;
                }
                break;

            case PLANET_TYPES.FOREST:
                height = this.noise.fbm(nx * 3, ny * 3, nz * 3, 4, 2.0, 0.5) * 0.15;
                height += 0.05;
                break;

            case PLANET_TYPES.ALIEN:
                const warp = this.noise.noise3D(nx * 2, ny * 2, nz * 2) * 0.5;
                height = this.noise.fbm(nx * 3 + warp, ny * 3 + warp, nz * 3 + warp, 5, 2.5, 0.5) * 0.35;
                height = Math.pow(Math.abs(height), 0.7) * Math.sign(height);
                break;

            default:
                height = this.noise.fbm(nx * 3, ny * 3, nz * 3, 4, 2.0, 0.5) * 0.2;
        }

        return height;
    }

    getVoxelColor(normalizedHeight, surfaceNormal) {
        const t = Utils.clamp((normalizedHeight + 0.5) / 1.0, 0, 1);

        if (this.type === PLANET_TYPES.WATER_WORLD) {
            if (normalizedHeight < 0.02) {
                return this.colors.deep.clone().lerp(this.colors.primary, t * 10);
            }
            return this.colors.accent.clone();
        }

        if (this.type === PLANET_TYPES.MOUNTAINOUS) {
            if (normalizedHeight > 0.5) return this.colors.accent.clone();
            if (normalizedHeight > 0.3) return this.colors.secondary.clone();
            if (normalizedHeight > 0.1) return this.colors.primary.clone();
            return this.colors.deep.clone();
        }

        if (this.type === PLANET_TYPES.VOLCANIC) {
            if (normalizedHeight > 0.4) return this.colors.accent.clone();
            return this.colors.primary.clone().lerp(this.colors.secondary, t);
        }

        return this.colors.primary.clone().lerp(this.colors.secondary, t);
    }

    generateLOD(lodLevel) {
        const resolution = Math.max(8, Math.floor(48 / (lodLevel + 1)));
        return this.generateSphereMesh(resolution, lodLevel);
    }

    generateSphereMesh(resolution, lodLevel) {
        const geometry = new THREE.BufferGeometry();
        const vertices = [];
        const colors = [];
        const normals = [];
        const indices = [];

        const detailScale = lodLevel === 0 ? 1.0 : (lodLevel === 1 ? 0.6 : 0.3);

        for (let lat = 0; lat <= resolution; lat++) {
            const theta = (lat / resolution) * Math.PI;
            const sinTheta = Math.sin(theta);
            const cosTheta = Math.cos(theta);

            for (let lon = 0; lon <= resolution * 2; lon++) {
                const phi = (lon / (resolution * 2)) * Math.PI * 2;
                const sinPhi = Math.sin(phi);
                const cosPhi = Math.cos(phi);

                const nx = sinTheta * cosPhi;
                const ny = cosTheta;
                const nz = sinTheta * sinPhi;

                const baseX = nx * this.radius;
                const baseY = ny * this.radius;
                const baseZ = nz * this.radius;

                let height = this.getTerrainHeight(baseX, baseY, baseZ) * detailScale;

                const r = this.radius * (1.0 + height);

                if (lodLevel === 0) {
                    const voxelR = Math.round(r / this.voxelSize) * this.voxelSize;
                    vertices.push(nx * voxelR, ny * voxelR, nz * voxelR);
                } else {
                    vertices.push(nx * r, ny * r, nz * r);
                }

                normals.push(nx, ny, nz);

                const color = this.getVoxelColor(height, new THREE.Vector3(nx, ny, nz));
                colors.push(color.r, color.g, color.b);
            }
        }

        for (let lat = 0; lat < resolution; lat++) {
            for (let lon = 0; lon < resolution * 2; lon++) {
                const a = lat * (resolution * 2 + 1) + lon;
                const b = a + resolution * 2 + 1;

                indices.push(a, b, a + 1);
                indices.push(b, b + 1, a + 1);
            }
        }

        geometry.setIndex(indices);
        geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
        geometry.setAttribute('normal', new THREE.Float32BufferAttribute(normals, 3));
        geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
        geometry.computeVertexNormals();

        const material = new THREE.MeshPhongMaterial({
            vertexColors: true,
            flatShading: lodLevel === 0,
            shininess: this.type === PLANET_TYPES.WATER_WORLD ? 80 : 10,
            specular: this.type === PLANET_TYPES.WATER_WORLD
                ? new THREE.Color(0x333333) : new THREE.Color(0x111111)
        });

        const mesh = new THREE.Mesh(geometry, material);
        mesh.castShadow = true;
        mesh.receiveShadow = true;
        return mesh;
    }

    generateAtmosphere() {
        const atmosGeom = new THREE.SphereGeometry(this.radius * 1.15, 32, 32);
        const atmosMat = new THREE.ShaderMaterial({
            vertexShader: `
                varying vec3 vNormal;
                varying vec3 vPosition;
                void main() {
                    vNormal = normalize(normalMatrix * normal);
                    vPosition = (modelViewMatrix * vec4(position, 1.0)).xyz;
                    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
                }
            `,
            fragmentShader: `
                uniform vec3 atmosphereColor;
                uniform float intensity;
                varying vec3 vNormal;
                varying vec3 vPosition;
                void main() {
                    vec3 viewDir = normalize(-vPosition);
                    float fresnel = 1.0 - dot(viewDir, vNormal);
                    fresnel = pow(fresnel, 3.0) * intensity;
                    gl_FragColor = vec4(atmosphereColor, fresnel * 0.6);
                }
            `,
            uniforms: {
                atmosphereColor: { value: this.colors.atmosphere },
                intensity: { value: 1.5 }
            },
            transparent: true,
            side: THREE.BackSide,
            depthWrite: false
        });

        this.atmosphere = new THREE.Mesh(atmosGeom, atmosMat);
        this.group.add(this.atmosphere);
    }

    generate() {
        if (this.isGenerated) return;

        // Generate multiple LODs
        for (let lod = 0; lod < 3; lod++) {
            const mesh = this.generateLOD(lod);
            mesh.visible = lod === 2; // Start with lowest detail
            this.lodMeshes[lod] = mesh;
            this.group.add(mesh);
        }

        this.generateAtmosphere();

        // Add rotation axis tilt
        const rng = Utils.seededRandom(this.seed + 200);
        this.group.rotation.z = (rng() - 0.5) * 0.5;

        this.isGenerated = true;
    }

    updateLOD(cameraDistance) {
        const relDist = cameraDistance / this.radius;

        let targetLOD;
        if (relDist < 3) targetLOD = 0;
        else if (relDist < 8) targetLOD = 1;
        else targetLOD = 2;

        for (let lod = 0; lod < 3; lod++) {
            if (this.lodMeshes[lod]) {
                this.lodMeshes[lod].visible = (lod === targetLOD);
            }
        }
    }

    update(deltaTime) {
        // Slow rotation
        this.group.rotation.y += deltaTime * 0.01;
    }

    getWorldPosition() {
        return this.group.position.clone();
    }

    getSurfaceHeight(direction) {
        const x = direction.x * this.radius;
        const y = direction.y * this.radius;
        const z = direction.z * this.radius;
        const height = this.getTerrainHeight(x, y, z);
        return this.radius * (1.0 + height);
    }
}
