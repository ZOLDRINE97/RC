// Simple JavaScript code for ball animation
class Ball {
    constructor(x, y, radius, color) {
        this.x = x;
        this.y = y;
        this.radius = radius;
        this.color = color;
        this.vx = (Math.random() - 0.5) * 4;
        this.vy = (Math.random() - 0.5) * 4;
    }

    draw(ctx) {
        ctx.fillStyle = this.color;
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
        ctx.fill();
    }

    update(width, height) {
        this.x += this.vx;
        this.y += this.vy;

        if (this.x - this.radius < 0 || this.x + this.radius > width) {
            this.vx *= -1;
        }
        if (this.y - this.radius < 0 || this.y + this.radius > height) {
            this.vy *= -1;
        }
    }
}

const canvas = document.querySelector('canvas');
const ctx = canvas.getContext('2d');
const balls = [];

for (let i = 0; i < 5; i++) {
    balls.push(new Ball(Math.random() * canvas.width, Math.random() * canvas.height, 10, `hsl(${Math.random() * 360}, 100%, 50%)`));
}

function animate() {
    ctx.fillStyle = 'rgba(0, 0, 0, 0.1)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    balls.forEach(ball => {
        ball.update(canvas.width, canvas.height);
        ball.draw(ctx);
    });

    requestAnimationFrame(animate);
}

animate();