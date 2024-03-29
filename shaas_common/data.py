items = [
    dict(
        name="Фалафель",
        description="Фалафель - это прекрасная альтернатива мясу. Блюдо, представляет собой жареные во фритюре шарики из измельчённых бобовых, приправленных пряностями, листья молодого салата, томаты, свежий огурчик, фирменный соус 1FF и конечно тандырный лаваш.",
        price=280,
        proteins=16.98,
        fats=13.78,
        carbohydrates=79.72,
        calories=506.28
    ),
    dict(
        name="Турецкая шварма",
        description="Турецкая шварма - это рубленая котлетка-микс из говядины и мяса ягненка, маринованный огурчик, молодые листья салата, красный лук, сыр и соус \"Турция\" в тандырном лаваше.",
        price=350,
        proteins=52.1,
        carbohydrates=78.5,
        fats=54.5,
        calories=1113
    ),
    dict(
        name="Сирийская шварма",
        description="Сирийская шварма - блюдо из рубленой говядины, гурийской капусты, корейской моркови, фирменного соуса 1FF, немного перчика халапеньо и тандырный лаваш.",
        price=320,
        proteins=35.6,
        fats=57.2,
        carbohydrates=64.3,
        calories=879
    ),
    dict(
        name="Марокканская шварма",
        description="Марокканская шварма - это блюдо из куриной грудки в панировке, молодых листьев салата, гурийской капусты, томата, свежего огурчика, моркови по корейски и тандырного лаваша.",
        price=250,
        proteins=19.6,
        fats=49,
        carbohydrates=70.3,
        calories=620
    ),
    dict(
        name="Ливанская шварма",
        description="Ливанская шварма - мясо ягненка в нежнейшей пите со свежими томатами, молодыми листьями салата, свежим огурчиком, сыром, красным лучком, приправленная фирменным соусом 1FF.",
        price=320,
        proteins=32.5,
        fats=52.1,
        carbohydrates=62.2,
        calories=860
    ),
    dict(
        name="Иранская шварма",
        description="Иранская шварма - это блюдо из нежного куриного бедрышка, жареного на мангале, молодых листьев салата, томата, свежего огурчика, с фирменным соусом 1 FF в тандырном лаваше.",
        price=280,
        proteins=24.1,
        fats=42.9,
        carbohydrates=59.3,
        calories=725
    ),
    dict(
        name="Дурум кебаб",
        description="Дурум кебаб - это люля из баранины, рубленые томаты, зелень, красный лук с соусом BBQ, завернутые в горячий тандырный лаваш.",
        price=330,
        proteins=29.4,
        fats=36.1,
        carbohydrates=60.7,
        calories=696
    ),
    dict(
        name="Алжирская шварма",
        description="Алжирская шварма - это куриная грудка в панировке, молодые листья салата, томат, соус BBQ и фирменный соус 1FF, а также сыр, луковые колечки и тандырный лаваш.",
        price=310,
        proteins=31.3,
        fats=70.6,
        carbohydrates=67.4,
        calories=780
    ),
    dict(
        name="Иорданская шварма",
        description="Иорданская шварма - это сочетание из рубленой говядины, двух видов соуса : сладкий Чили и BBQ, свежего салата, а также: немного перчика халапеньо, сыр и тандырный лаваш.",
        price=370,
        proteins=43.3,
        fats=80.3,
        carbohydrates=59.34,
        calories=1017
    ),
    dict(
        name="Брискет бургер",
        description="Брискет бургер - это сочетание копченой говяжьей грудинки с соусом гуакамоле, зернистой горчицей, белым соусом, соусом BBQ, листьями салата и сыром чеддер.",
        price=490,
        proteins=71.2,
        fats=80.4,
        carbohydrates=30.0,
        calories=745.6
    ),
    dict(
        name="Роял бургер",
        description="Роял бургер это две говяжьи котлетки, жареные на мангале, сыр чеддер, красный лучок, молодые листья салата и фирменный соус 1FF.",
        price=440,
        proteins=62,
        fats=34,
        carbohydrates=51,
        calories=620
    ),
    dict(
        name="Стрит бургер",
        description="Стрит бургер - это говяжья котлетка приготовления на огне, маринованный огурчик, молодые листья салата, томат, соус BBQ и фирменный соус 1FF.",
        price=320,
        proteins=30,
        fats=29,
        carbohydrates=42,
        calories=555
    ),
    dict(
        name="Терияки бургер",
        description="Терияки бургер это нежное куриное бёдрышко жареное на мангале, молодые листья салата, свежий огурчик, томат и соус терияки.",
        price=280,
        proteins=30,
        fats=11,
        carbohydrates=24,
        calories=430
    ),
    dict(
        name="Фиш бургер",
        description="Фиш бургер - это нежный и легкий бургер с рыбой. Для его приготовления используется хек в панировке, свежие и соленые огурчики, листья салата, творожный сыр и наш фирменный белый соус.",
        price=300,
        proteins=30,
        fats=28.7,
        carbohydrates=54.0,
        calories=640
    ),
]

for row in items:
    print(
        f"Имя: {row['name']}\n"
        f"Описание: {row['description']}\n"
        f"Цена: {row['price']}\n"
        f"Белки: {row['proteins']}\n"
        f"Жиры: {row['fats']}\n"
        f"Углеводы: {row['carbohydrates']}\n"
        f"ККал: {row['calories']}\n"
    )