from googletrans import Translator
from random import choices

async def text_translator(text):
    translator = Translator()
    recipe = translator.translate(text, dest='ru')
    return recipe.text


async def name_translator(text):
    translator = Translator()
    recipe = translator.translate(text, dest='en')
    return recipe.text


async def category(session):
    async with session.get(
        url=f'https://www.themealdb.com/api/json/v1/1/list.php?c=list',
    ) as resp:
        data = await resp.json()
        categories = [meal['strCategory'] for meal in data['meals']]
        return categories


async def name(session, name):
    async with session.get(
        url=f'https://www.themealdb.com/api/json/v1/1/search.php?s={await name_translator(name)}',
    ) as resp:
        data = await resp.json()
        if data['meals']:
            meal = data['meals'][0]
            meal_name = await text_translator(meal['strMeal'])
            ingredients = [(await text_translator(meal[f'strIngredient{i}']), meal[f'strMeasure{i}']) for i in range(1, 10) if meal[f'strIngredient{i}']]
            instructions = await text_translator(meal['strInstructions'])

            # Formatting the recipe text
            formatted_recipe = f"**{meal_name}**\n\n"
            formatted_recipe += "**Ингредиенты:**\n"
            for ingredient, measure in ingredients:
                formatted_recipe += f"- {measure} {ingredient}\n"
            formatted_recipe += "\n**Инструкции:**\n"
            formatted_recipe += instructions.replace('\r\n', '\n') + '\n\n'
            return formatted_recipe
        else:
            return "Рецепт не найден."


async def formated_recipe(recipe):
    if recipe['meals']:
        meal = recipe['meals'][0]
        meal_name = await text_translator(meal['strMeal'])
        ingredients = [(await text_translator(meal[f'strIngredient{i}']), meal[f'strMeasure{i}']) for i in range(1, 10) if meal[f'strIngredient{i}']]
        instructions = await text_translator(meal['strInstructions'])

        # Formatting the recipe text
        formatted_recipe = f"**{meal_name}**\n\n"
        formatted_recipe += "**Ингредиенты:**\n"
        for ingredient, measure in ingredients:
            formatted_recipe += f"- {measure} {ingredient}\n"
        formatted_recipe += "\n**Инструкции:**\n"
        formatted_recipe += instructions.replace('\r\n', '\n') + '\n\n'
        return formatted_recipe


async def recipe_by_category(session, category, quantity):
    async with session.get(
            url=f'https://www.themealdb.com/api/json/v1/1/filter.php?c={category}',
    ) as resp:
        data = await resp.json()

        names = [meal['strMeal'] for meal in data['meals']]
        ids = [ids['idMeal'] for ids in data['meals']]

        name_id = dict(zip(names, ids))

        random_name = choices(names, k=quantity['quantity'])
        message =[]
        random_id = []
        for key in random_name:
            value = name_id.get(key)
            random_id.append(value)

        translator = Translator()
        for name in random_name:
            tranlate = translator.translate(name, dest='ru').text
            message.append(tranlate)
    return message, random_id


async def id_reciep(session, ids):
    meals = []
    for reciep in ids.values():
        for id_rec in reciep:
            async with session.get(
              url=f'https://www.themealdb.com/api/json/v1/1/lookup.php?i={id_rec}',
            ) as resp:
                data = await resp.json()
                textes = await formated_recipe(data)
                meals.append(textes)

    return meals


