let shawa = [
    {
        name: "Фалафель",
        texture: PIXI.Texture.from("item15.jpeg")
    },
    {
        name: "Турецкая шварма",
        texture: PIXI.Texture.from("item16.jpeg")
    },
    {
        name: "Сирийская шварма",
        texture: PIXI.Texture.from("item17.jpeg")
    },
    {
        name: "Марокканская шварма",
        texture: PIXI.Texture.from("item18.jpeg")
    },
    {
        name: "Ливанская шварма",
        texture: PIXI.Texture.from("item19.jpeg")
    },
    {
        name: "Иранская шварма",
        texture: PIXI.Texture.from("item20.jpeg")
    },
    {
        name: "Дурум кебаб",
        texture: PIXI.Texture.from("item21.jpeg")
    },
    {
        name: "Алжирская шварма",
        texture: PIXI.Texture.from("item22.jpeg")
    },
    {
        name: "Иорданская шварма",
        texture: PIXI.Texture.from("item23.jpeg")
    },
    {
        name: "Брискет бургер",
        texture: PIXI.Texture.from("item24.jpeg")
    },
    {
        name: "Роял бургер",
        texture: PIXI.Texture.from("item25.jpeg")
    },
    {
        name: "Стрит бургер",
        texture: PIXI.Texture.from("item26.jpeg")
    },
    {
        name: "Терияки бургер",
        texture: PIXI.Texture.from("item27.jpeg")
    },
    {
        name: "Фиш бургер",
        texture: PIXI.Texture.from("item28.jpeg")
    },
];
let spiciness = [
    0x33ff99,
    0xffff66,
    0xff3333
]

let image_width = 675;
let image_height = 450;

function max(a, b) {
    if(a > b) return a;
    return b;
}

function getRandomInt(max) {
  return Math.floor(Math.random() * max);
}