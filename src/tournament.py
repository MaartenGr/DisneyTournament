import math
from PIL import Image, ImageDraw, ImageFont
from preprocessing import combine_rotten_and_imdb
from imdb_scraper import scrape


def create_disney_vs_pixar_main(df_left, df_right):
    """ Create the main disney vs pixar (16 vs. 16) matches """
    left_matches = create_matchup(df_left.sort_values("Seed_Score").tail(16))
    right_matches = create_matchup(df_right.sort_values("Seed_Score").tail(16))

    pattern, draw, font = init_pattern()
    pattern = create_left_bracket(left_matches, pattern, draw, font)
    pattern = create_right_bracket(right_matches, pattern, draw, font)

    return pattern


def create_all_disney_group_tournament(df):
    """ Create the full disney group tournament """
    titles = df.sort_values("Seed_Score").Title.values
    first = list(titles[len(titles) - 16:])[::-1]
    second = list(titles[len(titles) - 32:len(titles) - 16])[::-1]
    third = list(titles[len(titles) - 48:len(titles) - 32])[::-1]
    fourth = list(titles[:10])[::-1]

    matches = []
    for match_index in range(16):
        if len(fourth) == 0:
            matches.append((first.pop(0), second.pop(0), third.pop(0)))
        else:
            matches.append((first.pop(0), second.pop(0), third.pop(0), fourth.pop(0)))

    try:
        pattern = Image.open("../images/protected/disney_group_new.png", "r").convert('RGBA')
    except:
        pattern = Image.open("../images/unprotected/disney_group_new.png", "r").convert('RGBA')
    draw = ImageDraw.Draw(pattern, 'RGBA')
    font = ImageFont.truetype("../font/quicksand_bold.ttf", 34)

    height_text = 500
    height_diff = 117
    width_text = 285
    width_im = 170

    column = 0
    row = 0

    for index, group in enumerate(matches):

        for title in group:

            # Circle
            title_clean = (
                            title.lower()
                                 .replace("·", " ")
                                 .replace(",", " ")
                                 .replace(".", " ")
                                 .replace("'", " ")
                                 .strip()
                                 .replace("  ", " ")
            )
            title_clean = title_clean.replace("& ", "").replace(":", "").replace("-", " ")
            try:
                title_image = Image.open(f"../images/thumbnails/{title_clean}.png").convert('RGBA')
            except:
                title_image = Image.open(f"../images/empty.png").convert('RGBA')
            title_image = title_image.resize((105, 105), Image.ANTIALIAS)
            pattern.paste(title_image, (width_im, height_text - 28), mask=title_image)

            # Shorten text if too long
            width_title = font.getsize(title)[0]

            if width_title <= 250:
                draw.text((width_text, height_text), title, fill=(0, 0, 0), font=font)

            else:
                split = False
                size = 34
                while width_title > 250:
                    size -= 1
                    small_font = ImageFont.truetype("../font/quicksand_bold.ttf", size)
                    width_title = small_font.getsize(title)[0]

                    if size == 22:
                        tokens = title.split(" ")
                        split_length = int(math.floor(len(tokens) / 2))
                        title = " ".join(tokens[:split_length]) + "\n" + " ".join(tokens[split_length:])
                        split = True
                        break
                if split:
                    draw.text((width_text, height_text - 8), title, fill=(0, 0, 0), font=small_font)
                else:
                    draw.text((width_text, height_text), title, fill=(0, 0, 0), font=small_font)

            height_text += height_diff

        column += 1

        if column == 6:
            row += 1
            column = 0
        elif index != len(matches)-1:
            if len(matches[index+1]) == 3 and len(matches[index]) == 4:
                row += 1
                column = 0

        height_text = 500 + (row * 645)
        width_text = 285 + (column * 495)
        width_im = 170 + (column * 495)

    return pattern


def create_all_pixar_group_tournament(df):
    """ Create the full pixar group tournament """
    titles = list(df.sort_values("Seed_Score", ascending=False).Title.values)
    first = titles[:16]
    second = titles[16:]

    matches = []
    for match_index in range(16):
        if len(second) == 0:
            matches.append([first.pop(0)])
        else:
            matches.append((first.pop(0), second.pop(0)))

    try:
        pattern = Image.open("../images/protected/pixar_right.png", "r").convert('RGBA')
    except:
        pattern = Image.open("../images/unprotected/pixar_right.png", "r").convert('RGBA')
    draw = ImageDraw.Draw(pattern, 'RGBA')
    font = ImageFont.truetype("../font/quicksand_bold.ttf", 34)

    height_text = 675
    height_diff = 117
    width_text = 290
    width_im = 170

    column = 0
    row = 0

    for index, group in enumerate(matches):

        for title in group:

            # Circle
            title_clean = title.lower().replace("·", " ").replace(",", " ").replace(".", " ").replace("'",
                                                                                                      " ").strip().replace(
                "  ", " ")
            title_clean = title_clean.replace("& ", "").replace(":", "").replace("-", " ")
            try:
                title_image = Image.open(f"../images/thumbnails/{title_clean}.png").convert('RGBA')
            except:
                title_image = Image.open(f"../images/empty.png").convert('RGBA')
            title_image = title_image.resize((105, 105), Image.ANTIALIAS)
            pattern.paste(title_image, (width_im, height_text - 28), mask=title_image)

            # Shorten text if too long
            width_title = font.getsize(title)[0]

            if width_title <= 250:
                draw.text((width_text, height_text), title, fill=(0, 0, 0), font=font)

            else:
                split = False
                size = 34
                while width_title > 250:
                    size -= 1
                    small_font = ImageFont.truetype("../font/quicksand_bold.ttf", size)
                    width_title = small_font.getsize(title)[0]

                    if size == 22:
                        tokens = title.split(" ")
                        split_length = int(math.floor(len(tokens) / 2))
                        title = " ".join(tokens[:split_length]) + "\n" + " ".join(tokens[split_length:])
                        split = True
                        break
                if split:
                    draw.text((width_text, height_text - 8), title, fill=(0, 0, 0), font=small_font)
                else:
                    draw.text((width_text, height_text), title, fill=(0, 0, 0), font=small_font)

            height_text += height_diff

        column += 1

        if column == 6:
            row += 1
            column = 0
        elif index != len(matches) - 1:
            if len(matches[index + 1]) == 3 and len(matches[index]) == 4:
                row += 1
                column = 0

        height_text = 675 + (row * 530)
        width_text = 290 + (column * 495)
        width_im = 170 + (column * 495)

    return pattern


def create_disney_free_for_all_group_tournament(df, even=True):
    """ Create the Disney Free for All Group Tournament """
    if even:
        val = 0
    else:
        val = 1

    titles = df.sort_values("Seed_Score", ascending=False).Title.values
    titles = [title for index, title in enumerate(titles) if index % 2 == val]
    first = titles[:16]
    second = titles[16:]

    matches = []
    for match_index in range(16):
        if len(second) == 0:
            matches.append([first.pop(0)])
        else:
            matches.append((first.pop(0), second.pop(0)))

    if even:
        try:
            pattern = Image.open("../images/protected/disney_left.png", "r").convert('RGBA')
        except:
            pattern = Image.open("../images/unprotected/disney_left.png", "r").convert('RGBA')
    else:
        try:
            pattern = Image.open("../images/protected/disney_right.png", "r").convert('RGBA')
        except:
            pattern = Image.open("../images/unprotected/disney_right.png", "r").convert('RGBA')
    draw = ImageDraw.Draw(pattern, 'RGBA')
    font = ImageFont.truetype("../font/quicksand_bold.ttf", 34)

    height_text = 675
    height_diff = 117
    width_text = 290
    width_im = 170

    column = 0
    row = 0

    for index, group in enumerate(matches):

        for title in group:

            # Circle
            title_clean = title.lower().replace("·", " ").replace(",", " ").replace(".", " ").replace("'",
                                                                                                      " ").strip().replace(
                "  ", " ")
            title_clean = title_clean.replace("& ", "").replace(":", "").replace("-", " ")
            try:
                title_image = Image.open(f"../images/thumbnails/{title_clean}.png").convert('RGBA')
            except:
                title_image = Image.open(f"../images/empty.png").convert('RGBA')
            title_image = title_image.resize((105, 105), Image.ANTIALIAS)
            pattern.paste(title_image, (width_im, height_text - 28), mask=title_image)

            # Shorten text if too long
            width_title = font.getsize(title)[0]

            if width_title <= 250:
                draw.text((width_text, height_text), title, fill=(0, 0, 0), font=font)

            else:
                split = False
                size = 34
                while width_title > 250:
                    size -= 1
                    small_font = ImageFont.truetype("../font/quicksand_bold.ttf", size)
                    width_title = small_font.getsize(title)[0]

                    if size == 22:
                        tokens = title.split(" ")
                        split_length = int(math.floor(len(tokens) / 2))
                        title = " ".join(tokens[:split_length]) + "\n" + " ".join(tokens[split_length:])
                        split = True
                        break
                if split:
                    draw.text((width_text, height_text - 8), title, fill=(0, 0, 0), font=small_font)
                else:
                    draw.text((width_text, height_text), title, fill=(0, 0, 0), font=small_font)

            height_text += height_diff

        column += 1

        if column == 6:
            row += 1
            column = 0
        elif index != len(matches) - 1:
            if len(matches[index + 1]) == 3 and len(matches[index]) == 4:
                row += 1
                column = 0

        height_text = 675 + (row * 530)
        width_text = 290 + (column * 495)
        width_im = 170 + (column * 495)

    return pattern


def create_all_free_for_all_group_tournament(df):
    """ Create the All Free for All Group Tournament """
    titles = list(df.sort_values("Seed_Score", ascending=False).Title.values)
    left_titles = [title for index, title in enumerate(titles) if index % 2 == 0]
    right_titles = [title for index, title in enumerate(titles) if index % 2 != 0]

    left_pattern = create_8_groups(left_titles, left=True)
    right_pattern = create_8_groups(right_titles, left=False)

    return left_pattern, right_pattern


def create_rank_top_bottom_40(titles, scores, years, top=True):
    """ Create the Top and Bottom 40 of movies sorted by Seed Score """
    matches = [tuple(titles[x:x + 10]) for x in range(0, len(titles), 10)]
    scores = [round(score * 10, 1) for score in scores]
    scores = [tuple(scores[x:x + 10]) for x in range(0, len(scores), 10)]
    years = [tuple(years[x:x + 10]) for x in range(0, len(years), 10)]

    if top:
        try:
            pattern = Image.open("../images/protected/top_40.png", "r").convert('RGBA')
        except:
            pattern = Image.open("../images/unprotected/top_40.png", "r").convert('RGBA')
    else:
        try:
            pattern = Image.open("../images/protected/bottom_40.png", "r").convert('RGBA')
        except:
            pattern = Image.open("../images/unprotected/bottom_40.png", "r").convert('RGBA')
    circle = Image.open(f"../images/circle.png").convert('RGBA').resize((105, 105), Image.ANTIALIAS)

    draw = ImageDraw.Draw(pattern, 'RGBA')
    font = ImageFont.truetype("../font/quicksand_bold.ttf", 42)
    font_year = ImageFont.truetype("../font/quicksand_bold.ttf", 20)

    height_text = 607
    height_diff = 142

    width_text = 390
    width_im = 255
    width_diff = 745

    column = 0
    row = 0

    for group, score_group, years_tup in zip(matches, scores, years):

        for title, score, year in zip(group, score_group, years_tup):

            # Circle
            title_clean = title.lower().replace("·", " ").replace(",", " ").replace(".", " ").replace("'",
                                                                                                      " ").strip().replace(
                "  ", " ")
            title_clean = title_clean.replace("& ", "").replace(":", "").replace("-", " ")
            try:
                title_image = Image.open(f"../images/thumbnails/{title_clean}.png").convert('RGBA')
            except:
                title_image = Image.open(f"../images/empty.png").convert('RGBA')
            title_image = title_image.resize((120, 120), Image.ANTIALIAS)
            pattern.paste(title_image, (width_im, height_text - 28), mask=title_image)

            # Circle with score
            pattern.paste(circle, (width_im + 460, height_text - 20), mask=circle)
            font_score = ImageFont.truetype("../font/quicksand_bold.ttf", 48)
            if score < 2.0:
                draw.text((width_im + 485, height_text), str(score), fill=(0, 0, 0), font=font_score)
            else:
                draw.text((width_im + 475, height_text), str(score), fill=(0, 0, 0), font=font_score)

            # Shorten text if too long
            width_title = font.getsize(title)[0]

            if width_title <= 280:
                draw.text((width_text, height_text), title, fill=(0, 0, 0), font=font)

            else:
                split = False
                size = 42
                while width_title > 280:
                    size -= 1
                    small_font = ImageFont.truetype("../font/quicksand_bold.ttf", size)
                    width_title = small_font.getsize(title)[0]

                    if size == 30:
                        tokens = title.split(" ")
                        split_length = int(math.floor(len(tokens) / 2))
                        title = " ".join(tokens[:split_length]) + "\n" + " ".join(tokens[split_length:])
                        split = True
                        break
                if split:
                    draw.text((width_text, height_text - 10 + (size / 5)), title, fill=(0, 0, 0), font=small_font)
                else:
                    draw.text((width_text, height_text + (size / 4)), title, fill=(0, 0, 0), font=small_font)

            # Year
            year = str(int(year))
            draw.text((width_text + 280, height_text + 80), year, fill=(224, 224, 224), font=font_year)

            height_text += height_diff

        column += 1

        if column == 4:
            row += 1
            column = 0

        height_text = 607 + (row * 695)

        width_text = 390 + (column * width_diff)
        width_im = 255 + (column * width_diff)
    return pattern


def create_matchup(df):
    titles = df.sort_values("Seed_Score").Title.values
    nr_matches = int(len(titles) / 2)
    matches = [None for _ in range(nr_matches)]

    j = 0
    for i in range(nr_matches):
        if i % 2 == 0:
            matches[j] = (titles[i], titles[-1 - i])
        else:
            j += 1
            matches[-j] = (titles[i], titles[-1 - i])

    return matches


def init_pattern():
    try:
        pattern = Image.open("../images/protected/test_16_new.png", "r").convert('RGBA')
    except:
        pattern = Image.open("../images/unprotected/test_16_new.png", "r").convert('RGBA')
    draw = ImageDraw.Draw(pattern, 'RGBA')
    font = ImageFont.truetype("../font/quicksand_bold.ttf", 42)
    return pattern, draw, font


def create_left_bracket(matches, pattern, draw, font):
    height_text = 145
    height_diff = 136
    width_text = 200

    for i, match in enumerate(matches[::-1][:8]):

        # Draw top name
        top = match[0]

        # Circle
        top_clean = top.lower().replace("·", " ").replace(",", " ").replace(".", " ").replace("'", " ").strip().replace(
            "  ", " ")
        top_clean = top_clean.replace("& ", "").replace(":", "").replace("-", " ")
        try:
            top_image = Image.open(f"../images/thumbnails/{top_clean}.png").convert('RGBA')
        except:
            top_image = Image.open(f"../images/empty.png").convert('RGBA')
        top_image = top_image.resize((115, 115), Image.ANTIALIAS)
        pattern.paste(top_image, (73, height_text - 28), mask=top_image)

        # Draw bottom name
        down = match[1]

        # Circle
        down_clean = down.lower().replace("·", " ").replace(",", " ").replace(".", " ").replace("'",
                                                                                                " ").strip().replace(
            "  ", " ")
        down_clean = down_clean.replace("& ", "").replace(":", "").replace("-", " ")
        try:
            down_image = Image.open(f"../images/thumbnails/{down_clean}.png").convert('RGBA')
        except:
            down_image = Image.open(f"../images/empty.png").convert('RGBA')
        down_image = down_image.resize((115, 115), Image.ANTIALIAS)
        pattern.paste(down_image, (73, height_diff + height_text - 28), mask=down_image)

        # Shorten text if too long
        width_down = font.getsize(down)[0]
        while width_down > 300:
            down = down[0:-2] + "."
            width_down = font.getsize(down)[0]

        # Shorten text if too long
        width_top = font.getsize(top)[0]
        while width_top > 300:
            top = top[0:-2] + "."
            width_top = font.getsize(top)[0]

        draw.text((width_text, height_text), top, fill=(0, 0, 0), font=font)
        draw.text((width_text, height_diff + height_text), down, fill=(0, 0, 0), font=font)

        height_text += 272

    return pattern


def create_right_bracket(matches, pattern, draw, font):
    height_text = 147
    height_diff = 136

    width_text = 3155

    for i, match in enumerate(matches[:8]):

        # Draw top name
        top = match[0]
        down = match[1]

        # Circle top
        top_clean = top.lower().replace("·", " ").replace(",", " ").replace(".", " ").replace("'", " ").strip().replace(
            "  ", " ")
        top_clean = top_clean.replace("& ", "").replace(":", "").replace("-", " ")
        try:
            top_image = Image.open(f"../images/thumbnails/{top_clean}.png").convert('RGBA')
        except:
            top_image = Image.open(f"../images/empty.png").convert('RGBA')
        top_image = top_image.resize((115, 115), Image.ANTIALIAS)
        pattern.paste(top_image, (3170, height_text - 28), mask=top_image)

        # Circle bottom
        down_clean = down.lower().replace("·", " ").replace(",", " ").replace(".", " ").replace("'",
                                                                                                " ").strip().replace(
            "  ", " ")
        down_clean = down_clean.replace("& ", "").replace(":", "").replace("-", " ")
        try:
            down_image = Image.open(f"../images/thumbnails/{down_clean}.png").convert('RGBA')
        except:
            down_image = Image.open(f"../images/empty.png").convert('RGBA')
        down_image = down_image.resize((115, 115), Image.ANTIALIAS)
        pattern.paste(down_image, (3170, height_diff + height_text - 28), mask=down_image)

        # Shorten text if too long
        width_down = font.getsize(down)[0]
        while width_down > 300:
            down = down[0:-2] + "."
            width_down = font.getsize(down)[0]

        # Shorten text if too long
        width_top = font.getsize(top)[0]
        while width_top > 300:
            top = top[0:-2] + "."
            width_top = font.getsize(top)[0]

        # Draw text on the right side
        text_width, text_height = draw.textsize(top, font)
        draw.text((width_text - text_width, height_text), top, fill=(0, 0, 0), font=font, align="right")

        text_width, text_height = draw.textsize(down, font)
        draw.text((width_text - text_width, height_diff + height_text), down, fill=(0, 0, 0), font=font)

        height_text += 272

    return pattern


def create_8_groups(titles, left=True):
    chunks = [list(titles[x:x + 8]) for x in range(0, len(titles), 8)]

    matches = []
    for match_index in range(8):
        matches.append((chunks[0].pop(0), chunks[1].pop(0), chunks[2].pop(0), chunks[3].pop(0), chunks[4].pop(0)))
    
    if left:
        try:
            pattern = Image.open("../images/protected/free_for_all_left.png", "r").convert('RGBA')
        except:
            pattern = Image.open("../images/unprotected/free_for_all_left.png", "r").convert('RGBA')
    else:
        try:
            pattern = Image.open("../images/protected/free_for_all_right.png", "r").convert('RGBA')
        except:
            pattern = Image.open("../images/unprotected/free_for_all_right.png", "r").convert('RGBA')

    draw = ImageDraw.Draw(pattern, 'RGBA')
    font = ImageFont.truetype("../font/quicksand_bold.ttf", 42)

    height_text = 543
    height_diff = 147

    width_text = 258
    width_im = 120

    width_diff = 645

    column = 0
    row = 0

    for group in matches:

        for title in group:

            # Circle
            title_clean = title.lower().replace("·", " ").replace(",", " ").replace(".", " ").replace("'",
                                                                                                      " ").strip().replace(
                "  ", " ")
            title_clean = title_clean.replace("& ", "").replace(":", "").replace("-", " ")
            try:
                title_image = Image.open(f"../images/thumbnails/{title_clean}.png").convert('RGBA')
            except:
                title_image = Image.open(f"../images/empty.png").convert('RGBA')
            title_image = title_image.resize((120, 120), Image.ANTIALIAS)
            pattern.paste(title_image, (width_im, height_text - 28), mask=title_image)

            # Shorten text if too long
            width_title = font.getsize(title)[0]

            if width_title <= 250:
                draw.text((width_text, height_text), title, fill=(0, 0, 0), font=font)

            else:
                split = False
                size = 42
                while width_title > 250:
                    size -= 1
                    small_font = ImageFont.truetype("../font/quicksand_bold.ttf", size)
                    width_title = small_font.getsize(title)[0]

                    if size == 30:
                        tokens = title.split(" ")
                        split_length = int(math.floor(len(tokens) / 2))
                        title = " ".join(tokens[:split_length]) + "\n" + " ".join(tokens[split_length:])
                        split = True
                        break
                        
                height_title = small_font.getsize(title)[1]

                if split:
                    draw.text((width_text, height_text - 5), title, fill=(0, 0, 0), font=small_font)
                else:
                    draw.text((width_text, height_text + (height_title/3)), title, fill=(0, 0, 0), font=small_font)

            height_text += height_diff

        column += 1

        if column == 4:
            row += 1
            column = 0

        height_text = 535 + (row * 930)

        width_text = 260 + (column * width_diff)
        width_im = 120 + (column * width_diff)

    return pattern








