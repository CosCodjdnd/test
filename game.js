const canvas = document.querySelector("#game");
const ctx = canvas.getContext("2d");

const hud = {
  score: document.querySelector("#score"),
  lives: document.querySelector("#lives"),
  level: document.querySelector("#level"),
};

const resetButton = document.querySelector("#reset");

const world = {
  width: 3600,
  height: canvas.height,
  gravity: 0.55,
  friction: 0.85,
};

const colors = {
  ground: "#3b285f",
  platform: "#5c3a82",
  coin: "#ffd15c",
  enemy: "#ff6b6b",
  player: "#5cf0ff",
  cloud: "rgba(255, 255, 255, 0.8)",
  tree: "#2f9e44",
  trunk: "#9a6b45",
};

const keys = new Set();

const player = {
  x: 120,
  y: 0,
  width: 42,
  height: 52,
  vx: 0,
  vy: 0,
  speed: 3.5,
  jump: 12,
  grounded: false,
  facing: 1,
  dashCooldown: 0,
};

const gameState = {
  score: 0,
  lives: 3,
  level: 1,
  scrollX: 0,
  message: "",
  messageTimer: 0,
};

const platforms = [
  { x: 0, y: 440, width: 520, height: 100 },
  { x: 580, y: 420, width: 260, height: 120 },
  { x: 940, y: 360, width: 220, height: 180 },
  { x: 1240, y: 410, width: 320, height: 130 },
  { x: 1680, y: 350, width: 260, height: 190 },
  { x: 2040, y: 420, width: 260, height: 120 },
  { x: 2380, y: 370, width: 280, height: 170 },
  { x: 2760, y: 430, width: 320, height: 110 },
  { x: 3140, y: 390, width: 320, height: 150 },
];

const coins = [
  { x: 260, y: 360, collected: false },
  { x: 640, y: 330, collected: false },
  { x: 980, y: 250, collected: false },
  { x: 1100, y: 280, collected: false },
  { x: 1480, y: 310, collected: false },
  { x: 1760, y: 240, collected: false },
  { x: 2140, y: 350, collected: false },
  { x: 2440, y: 280, collected: false },
  { x: 2900, y: 360, collected: false },
  { x: 3240, y: 310, collected: false },
];

const enemies = [
  { x: 720, y: 380, width: 42, height: 36, vx: 1.4, range: 120 },
  { x: 1520, y: 320, width: 42, height: 36, vx: 1.1, range: 150 },
  { x: 2620, y: 340, width: 42, height: 36, vx: 1.2, range: 130 },
];

enemies.forEach((enemy) => {
  enemy.startX = enemy.x;
});

const clouds = Array.from({ length: 8 }, (_, index) => ({
  x: index * 420 + 120,
  y: 80 + (index % 3) * 40,
  width: 120 + (index % 2) * 50,
  height: 40 + (index % 2) * 15,
}));

const scenery = [
  { x: 200, y: 360 },
  { x: 820, y: 340 },
  { x: 1380, y: 310 },
  { x: 2200, y: 350 },
  { x: 3000, y: 330 },
];

const resetGame = () => {
  player.x = 120;
  player.y = 0;
  player.vx = 0;
  player.vy = 0;
  player.grounded = false;
  player.facing = 1;
  player.dashCooldown = 0;

  gameState.score = 0;
  gameState.lives = 3;
  gameState.level = 1;
  gameState.scrollX = 0;
  gameState.message = "";
  gameState.messageTimer = 0;

  coins.forEach((coin) => {
    coin.collected = false;
  });

  enemies.forEach((enemy) => {
    enemy.x = enemy.startX;
  });

  updateHud();
};

const updateHud = () => {
  hud.score.textContent = gameState.score;
  hud.lives.textContent = gameState.lives;
  hud.level.textContent = gameState.level;
};

const showMessage = (text) => {
  gameState.message = text;
  gameState.messageTimer = 150;
};

const handleInput = () => {
  const left = keys.has("ArrowLeft") || keys.has("a");
  const right = keys.has("ArrowRight") || keys.has("d");
  const jump = keys.has(" ") || keys.has("ArrowUp") || keys.has("w");
  const dash = keys.has("Shift");

  if (left) {
    player.vx -= player.speed;
    player.facing = -1;
  }
  if (right) {
    player.vx += player.speed;
    player.facing = 1;
  }

  if (jump && player.grounded) {
    player.vy = -player.jump;
    player.grounded = false;
  }

  if (dash && player.dashCooldown <= 0) {
    player.vx += player.facing * 12;
    player.dashCooldown = 40;
    showMessage("Dash!");
  }
};

const applyPhysics = () => {
  player.vy += world.gravity;
  player.x += player.vx;
  player.y += player.vy;

  player.vx *= world.friction;
  player.vy *= 0.98;

  if (player.dashCooldown > 0) {
    player.dashCooldown -= 1;
  }

  if (player.x < 0) {
    player.x = 0;
    player.vx = 0;
  }

  if (player.x + player.width > world.width) {
    player.x = world.width - player.width;
    player.vx = 0;
  }

  player.grounded = false;
  platforms.forEach((platform) => {
    if (
      player.x + player.width > platform.x &&
      player.x < platform.x + platform.width &&
      player.y + player.height > platform.y &&
      player.y + player.height < platform.y + platform.height
    ) {
      player.y = platform.y - player.height;
      player.vy = 0;
      player.grounded = true;
    }
  });

  if (player.y + player.height > world.height) {
    player.y = world.height - player.height;
    player.vy = 0;
    player.grounded = true;
  }
};

const updateCamera = () => {
  const center = player.x - canvas.width / 2 + player.width / 2;
  gameState.scrollX = Math.min(
    Math.max(center, 0),
    world.width - canvas.width,
  );
};

const updateCoins = () => {
  coins.forEach((coin) => {
    if (coin.collected) return;
    const hit =
      player.x < coin.x + 18 &&
      player.x + player.width > coin.x - 18 &&
      player.y < coin.y + 18 &&
      player.y + player.height > coin.y - 18;
    if (hit) {
      coin.collected = true;
      gameState.score += 100;
      showMessage("Star shard collected!");
      updateHud();
    }
  });

  if (coins.every((coin) => coin.collected)) {
    gameState.level += 1;
    coins.forEach((coin) => {
      coin.collected = false;
    });
    gameState.score += 500;
    showMessage("Level up!");
    updateHud();
  }
};

const updateEnemies = () => {
  enemies.forEach((enemy) => {
    enemy.x += enemy.vx;
    if (Math.abs(enemy.x - enemy.startX) > enemy.range) {
      enemy.vx *= -1;
    }

    const hit =
      player.x < enemy.x + enemy.width &&
      player.x + player.width > enemy.x &&
      player.y < enemy.y + enemy.height &&
      player.y + player.height > enemy.y;

    if (hit) {
      if (player.vy > 1) {
        enemy.x = enemy.startX;
        gameState.score += 150;
        player.vy = -player.jump * 0.7;
        showMessage("Stomped!");
      } else {
        gameState.lives -= 1;
        showMessage("Ouch! -1 life");
        player.x = Math.max(0, player.x - 120);
        player.vy = -player.jump * 0.5;
        if (gameState.lives <= 0) {
          showMessage("Game over! Restart?");
          resetGame();
        }
      }
      updateHud();
    }
  });
};

const drawBackground = () => {
  ctx.fillStyle = "#6bc2ff";
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  clouds.forEach((cloud) => {
    const x = cloud.x - gameState.scrollX * 0.4;
    ctx.fillStyle = colors.cloud;
    ctx.beginPath();
    ctx.ellipse(x, cloud.y, cloud.width / 2, cloud.height / 2, 0, 0, Math.PI * 2);
    ctx.fill();
  });

  ctx.fillStyle = "#ffd86f";
  ctx.beginPath();
  ctx.arc(780 - gameState.scrollX * 0.2, 90, 40, 0, Math.PI * 2);
  ctx.fill();
};

const drawPlatforms = () => {
  platforms.forEach((platform) => {
    const x = platform.x - gameState.scrollX;
    ctx.fillStyle = colors.platform;
    ctx.fillRect(x, platform.y, platform.width, platform.height);
    ctx.fillStyle = colors.ground;
    ctx.fillRect(x, platform.y, platform.width, 12);
  });

  ctx.fillStyle = colors.ground;
  ctx.fillRect(-gameState.scrollX, world.height - 20, world.width, 20);
};

const drawScenery = () => {
  scenery.forEach((tree) => {
    const x = tree.x - gameState.scrollX * 0.8;
    ctx.fillStyle = colors.trunk;
    ctx.fillRect(x, tree.y, 22, 80);
    ctx.fillStyle = colors.tree;
    ctx.beginPath();
    ctx.arc(x + 11, tree.y, 40, 0, Math.PI * 2);
    ctx.fill();
  });
};

const drawCoins = () => {
  coins.forEach((coin) => {
    if (coin.collected) return;
    const x = coin.x - gameState.scrollX;
    ctx.strokeStyle = colors.coin;
    ctx.lineWidth = 4;
    ctx.beginPath();
    ctx.arc(x, coin.y, 14, 0, Math.PI * 2);
    ctx.stroke();
    ctx.fillStyle = "rgba(255, 209, 92, 0.4)";
    ctx.beginPath();
    ctx.arc(x, coin.y, 8, 0, Math.PI * 2);
    ctx.fill();
  });
};

const drawEnemies = () => {
  enemies.forEach((enemy) => {
    const x = enemy.x - gameState.scrollX;
    ctx.fillStyle = colors.enemy;
    ctx.fillRect(x, enemy.y, enemy.width, enemy.height);
    ctx.fillStyle = "rgba(0,0,0,0.35)";
    ctx.fillRect(x + 8, enemy.y + 10, 8, 8);
    ctx.fillRect(x + 26, enemy.y + 10, 8, 8);
  });
};

const drawPlayer = () => {
  const x = player.x - gameState.scrollX;
  ctx.fillStyle = colors.player;
  ctx.fillRect(x, player.y, player.width, player.height);

  ctx.fillStyle = "#0c2b38";
  ctx.fillRect(x + 8, player.y + 14, 8, 8);
  ctx.fillRect(x + player.width - 16, player.y + 14, 8, 8);

  ctx.fillStyle = "#ff8fab";
  ctx.fillRect(x + 10, player.y + 30, player.width - 20, 8);
};

const drawHudMessage = () => {
  if (gameState.messageTimer <= 0) return;
  ctx.fillStyle = "rgba(7, 12, 32, 0.7)";
  ctx.fillRect(20, 20, 260, 46);
  ctx.fillStyle = "#f9f4ff";
  ctx.font = "18px 'Trebuchet MS'";
  ctx.fillText(gameState.message, 32, 50);
  gameState.messageTimer -= 1;
};

const render = () => {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  drawBackground();
  drawScenery();
  drawPlatforms();
  drawCoins();
  drawEnemies();
  drawPlayer();
  drawHudMessage();
};

const update = () => {
  handleInput();
  applyPhysics();
  updateCamera();
  updateCoins();
  updateEnemies();
  render();
  requestAnimationFrame(update);
};

window.addEventListener("keydown", (event) => {
  keys.add(event.key);
});

window.addEventListener("keyup", (event) => {
  keys.delete(event.key);
});

resetButton.addEventListener("click", resetGame);

resetGame();
update();
