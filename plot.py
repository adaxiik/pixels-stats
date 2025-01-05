import json
import sys
from dataclasses import dataclass
from datetime import datetime

import matplotlib.pyplot as plt
import seaborn as sns
from functional import seq


@dataclass
class Mood:
    type: str
    date: datetime
    score: int
    notes: str

    @staticmethod
    def from_dict(data: dict) -> "Mood":
        return Mood(
            type=data.get("type"),
            date=datetime.strptime(data.get("date"), "%Y-%m-%d"),
            score=int(data.get("scores")[0]),
            notes=data.get("notes"),
        )


def smooth_moods(moods: list[Mood], window_size: int) -> list[Mood]:
    smoothed_moods = []
    for i in range(len(moods)):
        start = max(0, i - window_size)
        end = min(len(moods), i + window_size)
        window = moods[start:end]
        score = sum([mood.score for mood in window]) / len(window)
        smoothed_moods.append(
            Mood(
                type=moods[i].type,
                date=moods[i].date,
                score=score,
                notes=moods[i].notes,
            )
        )
    return smoothed_moods


def smooth_note_len(moods: list[Mood], window_size: int) -> list[tuple[datetime, int]]:
    smoothed_notes = []
    for i in range(len(moods)):
        start = max(0, i - window_size)
        end = min(len(moods), i + window_size)
        window = moods[start:end]
        note_len = sum([len(mood.notes) for mood in window]) / len(window)
        smoothed_notes.append((moods[i].date, note_len))
    return smoothed_notes


def smooth_ints(ints: list[int], window_size: int) -> list[int]:
    smoothed_ints = []
    for i in range(len(ints)):
        start = max(0, i - window_size)
        end = min(len(ints), i + window_size)
        window = ints[start:end]
        smoothed_ints.append(sum(window) / len(window))
    return smoothed_ints


def avg(iterable, key=None):
    if key is None:
        key = lambda x: x
    return sum([key(x) for x in iterable]) / len(iterable)


def plot_mood_in_time(moods: list[Mood]):
    moods = smooth_moods(moods, 60)
    sns.lineplot(x=[mood.date for mood in moods], y=[mood.score for mood in moods])
    plt.legend(["Mood"])
    plt.title("Mood in Time")
    plt.xlabel("Date")
    plt.ylabel("Score")
    dates = (
        seq([mood.date for mood in moods])
        .group_by(lambda x: (x.year, x.month))
        .map(lambda x: x[1][0])
        .map(lambda x: x.strftime("%Y-%m"))
        .to_list()
    )

    plt.xticks(ticks=dates, labels=dates, rotation=45)

    plt.show()


def plot_top_moods(moods: list[Mood], n: int):
    top_moods = (
        seq(moods)
        .group_by(lambda x: (x.date.year, x.date.month))
        .map(lambda x: (x[0], avg(x[1], key=lambda y: y.score)))
        .sorted(key=lambda x: x[1], reverse=True)
        .take(n)
        .to_list()
    )

    sns.barplot(
        x=[f"{x[0][0]}-{x[0][1]}" for x in top_moods], y=[x[1] for x in top_moods]
    )
    plt.title("Top Moods")
    plt.xlabel("Month")
    plt.ylabel("Score")
    plt.show()


def plot_worst_moods(moods: list[Mood], n: int):
    worst_moods = (
        seq(moods)
        .group_by(lambda x: (x.date.year, x.date.month))
        .map(lambda x: (x[0], avg(x[1], key=lambda y: y.score)))
        .sorted(key=lambda x: x[1])
        .take(n)
        .to_list()
    )

    sns.barplot(
        x=[f"{x[0][0]}-{x[0][1]}" for x in worst_moods], y=[x[1] for x in worst_moods]
    )
    plt.title("Worst Moods")
    plt.xlabel("Month")
    plt.ylabel("Score")
    plt.show()


def plot_top_longest_notes(moods: list[Mood], n: int):
    top_notes = (
        seq(moods).sorted(key=lambda x: len(x.notes), reverse=True).take(n).to_list()
    )

    sns.barplot(x=[x.date for x in top_notes], y=[len(x.notes) for x in top_notes])
    plt.title("Top Longest Notes")
    plt.xlabel("Date")
    plt.ylabel("Length")
    plt.show()


def plot_note_len_in_time(moods: list[Mood]):
    smoothed_notes = smooth_note_len(moods, 14)
    sns.lineplot(x=[x[0] for x in smoothed_notes], y=[x[1] for x in smoothed_notes])
    plt.legend(["Note Length"])
    plt.title("Note Length in Time")
    plt.xlabel("Date")
    plt.ylabel("Length")
    dates = (
        seq([x[0] for x in smoothed_notes])
        .group_by(lambda x: (x.year, x.month))
        .map(lambda x: x[1][0])
        .map(lambda x: x.strftime("%Y-%m"))
        .to_list()
    )

    plt.xticks(ticks=dates, labels=dates, rotation=45)

    plt.show()


def plot_days_containing_words(moods: list[Mood], words: set[str]):
    words = set([word.lower() for word in words])

    word_count = (
        seq(moods)
        .map(lambda x: (x.date, sum([1 for word in words if word in x.notes.lower()])))
        .to_list()
    )

    smoothed_word_count = smooth_ints([x[1] for x in word_count], 14)
    sns.lineplot(x=[x[0] for x in word_count], y=smoothed_word_count)

    plt.legend(["Word Count"])
    plt.title(f'Days Containing Words: {", ".join(words)}')
    plt.xlabel("Date")
    plt.ylabel("Count")

    dates = (
        seq([x[0] for x in word_count])
        .group_by(lambda x: (x.year, x.month))
        .map(lambda x: x[1][0])
        .map(lambda x: x.strftime("%Y-%m"))
        .to_list()
    )

    plt.xticks(ticks=dates, labels=dates, rotation=45)

    plt.show()


moods: list[Mood] = [Mood.from_dict(x) for x in json.loads(sys.stdin.read())]
moods.sort(key=lambda x: x.date)

sns.set_theme(style="darkgrid", context="notebook")
plot_mood_in_time(moods)
plot_top_moods(moods, 5)
plot_worst_moods(moods, 5)
plot_top_longest_notes(moods, 10)
plot_note_len_in_time(moods)
plot_days_containing_words(moods, {"word"})
