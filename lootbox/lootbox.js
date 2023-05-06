let app = new PIXI.Application({
    width: window.innerWidth,
    height: window.innerHeight,
    backgroundColor: 0xffffff
});

let spinningState = 0;

let containers = [];

calc_width = app.screen.width / 3
calc_height = image_height * (calc_width / image_width)

console.log(calc_width + " " + calc_height)

let card_count = Math.floor(app.screen.height / calc_height)

for(let i = 0; i < card_count; i++) {
    data = shawa[getRandomInt(shawa.length)]
    const container = new PIXI.Container();

    container.x = app.screen.width / 2 - calc_width / 2;
    container.y = (calc_height + 10) * i ;

    sprite = new PIXI.Sprite(data.texture);
    sprite.width = calc_width;
    sprite.height = calc_height;
    container.addChild(sprite);

    let obj = new PIXI.Graphics();
    obj.beginFill(0xffffff);
    let spicy = getRandomInt(spiciness.length)
    obj.tint = spiciness[spicy]
    obj.drawRect(0, calc_height - 10, calc_width, 10);
    container.addChild(obj);

    app.stage.addChild(container);
    containers.push({
        container: container,
        sprite: sprite,
        line: obj,
        name: data.name,
        spicy: spicy
    });
}

const radius = (app.screen.height) / 4;
const blurSize = 500;
const circle = new PIXI.Graphics()
        .beginFill(0xFF0000)
        .drawCircle(radius + blurSize, radius + blurSize, radius)
        .endFill();
let blurFilter = new PIXI.BlurFilter(blurSize);
blurFilter.blur = 40
circle.filters = [blurFilter]
const bounds = new PIXI.Rectangle(0, 0, (radius + blurSize) * 2, (radius + blurSize) * 2);
const texture = app.renderer.generateTexture(circle, PIXI.SCALE_MODES.NEAREST, 1, bounds);
const focus = new PIXI.Sprite(texture);
focus.x = app.screen.width / 2 - focus.width / 2
focus.y = app.screen.height / 2 - focus.height / 2
app.stage.addChild(focus);
app.stage.mask = focus



// const button = new PIXI.Text('Лутарня!');
// button.x = app.screen.width / 2 - button.width / 2;
// button.y = app.screen.height - 50;
// button.interactive = true;
// button.buttonMode = true;
// button.on('pointerdown', (event) => {
//     spinningState = 1;
//     button.visible = false;
//     elapsed = 0;
//     result.visible = false;
// })
// app.stage.addChild(button);
//
// const result = new PIXI.Text("Нажмите кнопку и откройте лутбокс!");
// result.x = app.screen.width / 2 - result.width / 2;
// result.y = 10;
// app.stage.addChild(result);
//
// let separator = new PIXI.Graphics();
// separator.beginFill(0xffff99);
// separator.drawRect(0, 0, 10, image_height * 2);
// separator.x = app.screen.width / 2 - 5
// separator.y = app.screen.height / 2 - image_height
// separator.alpha = 0.5
// app.stage.addChild(separator);


// Add a variable to count up the seconds our demo has been running
let elapsed = 0.0;
let max_speed = 0.0;
// Tell our application's ticker to run a new callback every frame, passing
// in the amount of time that has passed since the last tick
app.ticker.add((delta) => {
    elapsed += delta;

    // console.log(elapsed)
    if(spinningState === 0) return;
    if(spinningState === 1 && elapsed > 50) {
        max_speed = elapsed;
        elapsed = 0;
        spinningState = 2;
    }
    if(spinningState === 2 && elapsed > 1000) {
        spinningState = 0;

        for(let i = 0; i < c_count; i++) {
            if(containers[i].container.x <= app.screen.width / 2 && app.screen.width / 2 < containers[i].container.x + containers[i].container.width) {
                console.log(containers[i].name)
                let spicy_str = "обычная"
                switch (containers[i].spicy) {
                    case 0:
                        spicy_str = "без острого";
                        break
                    case 1:
                        spicy_str = "без изменений"
                        break
                    case 2:
                        spicy_str = "поострее!"
                        break
                }
                button.visible = true;
                result.text = "Заказ: " + containers[i].name + "\nОстрота: " + spicy_str
                result.x = app.screen.width / 2 - result.width / 2;
                result.visible = true;
            }
        }
    }

    let max_offset = 0;
    for(let i = 0; i < c_count; i++) {
        switch(spinningState) {
            case 1:
                containers[i].container.x -= elapsed;
                break;
            case 2:
                containers[i].container.x -= (-max_speed/1000) * elapsed + max_speed
                break
        }

        max_offset = max(max_offset, containers[i].container.x + containers[i].container.width + 10)
    }

    for(let i = 0; i < c_count; i++) {
        if(containers[i].container.x + containers[i].container.width + 10 < 0) {
            containers[i].container.x = max_offset
            max_offset += containers[i].container.width + 10

            let data = shawa[getRandomInt(shawa.length)]
            let spicy = getRandomInt(spiciness.length)
            containers[i].sprite.texture = data.texture
            containers[i].line.tint = spiciness[spicy]
            containers[i].name = data.name
            containers[i].spicy = spicy
        }
    }
});

document.body.appendChild(app.view);