from preprocessing import combine_rotten_and_imdb
from tournament import (create_disney_vs_pixar_main,
                        create_all_disney_group_tournament,
                        create_all_free_for_all_group_tournament,
                        create_rank_top_bottom_40,
                        create_disney_free_for_all_group_tournament,
                        create_all_pixar_group_tournament)


def main():
    pixar, disney, total = combine_rotten_and_imdb()

    # Create Images
    disney_vs_pixar_main = create_disney_vs_pixar_main(pixar, disney)
    all_disney_group_tournament = create_all_disney_group_tournament(disney)
    all_pixar_group_tournament = create_all_pixar_group_tournament(pixar)
    disney_free_for_all_left = create_disney_free_for_all_group_tournament(disney, even=True)
    disney_free_for_all_right = create_disney_free_for_all_group_tournament(disney, even=False)
    free_for_all_left, free_for_all_right = create_all_free_for_all_group_tournament(total)

    top_40 = create_rank_top_bottom_40(total.sort_values("Seed_Score", ascending=False).Title.values[:40],
                                       total.sort_values("Seed_Score", ascending=False).Seed_Score.values[:40],
                                       total.sort_values("Seed_Score", ascending=False).Year.values[:40],
                                       top=True)

    bottom_40 = create_rank_top_bottom_40(total.sort_values("Seed_Score", ascending=False).Title.values[40:],
                                          total.sort_values("Seed_Score", ascending=False).Seed_Score.values[40:],
                                          total.sort_values("Seed_Score", ascending=False).Year.values[40:],
                                          top=False)

    # Save results
    disney_vs_pixar_main.save("../images/results/main.png")
    all_disney_group_tournament.save("../images/results/all_disney_group_tournament.png")
    all_pixar_group_tournament.save("../images/results/all_pixar_group_tournament.png")
    disney_free_for_all_left.save("../images/results/disney_free_for_all_left.png")
    disney_free_for_all_right.save("../images/results/disney_free_for_all_right.png")
    free_for_all_left.save("../images/results/free_for_all_left.png")
    free_for_all_right.save("../images/results/free_for_all_right.png")
    top_40.save("../images/results/top_40.png")
    bottom_40.save("../images/results/bottom_40.png")


if __name__ == "__main__":
    main()
