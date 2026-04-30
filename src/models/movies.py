import uuid as python_uuid
from decimal import Decimal

from sqlalchemy import String, Table, Integer, Float, Text, DECIMAL, ForeignKey, UniqueConstraint, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from src.db.base import Base


movie_genres = Table(
    "movie_genres",
    Base.metadata,
    Column("movie_id", ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True),
    Column("genre_id", ForeignKey("genres.id", ondelete="CASCADE"), primary_key=True),
)

movie_stars = Table(
    "movie_stars",
    Base.metadata,
    Column("movie_id", ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True),
    Column("star_id", ForeignKey("stars.id", ondelete="CASCADE"), primary_key=True)
)

movie_directors = Table(
    "movie_directors",
    Base.metadata,
    Column("movie_id", ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True),
    Column("director_id", ForeignKey("directors.id", ondelete="CASCADE"), primary_key=True),
)

favorite_movies = Table(
    "favorite_movies",
    Base.metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("movie_id", ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True)
)


class Genre(Base):
    __tablename__ = "genres"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False
    )

    movies: Mapped[list["Movie"]] = relationship(
        secondary=movie_genres,
        back_populates="genres"
    )


class Star(Base):
    __tablename__ = "stars"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(
        String(150),
        unique=True,
        nullable=False
    )

    movies: Mapped[list["Movie"]] = relationship(
        secondary=movie_stars,
        back_populates="stars"
    )


class Director(Base):
    __tablename__ = "directors"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(
        String(150),
        unique=True,
        nullable=False
    )

    movies: Mapped[list["Movie"]] = relationship(
        secondary=movie_directors,
        back_populates="directors"
    )


class Certification(Base):
    __tablename__ = "certifications"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False
    )

    movies: Mapped[list["Movie"]] = relationship(
        back_populates="certification"
    )


class Movie(Base):
    __tablename__ = "movies"
    __table_args__ = (
        UniqueConstraint(
            "name", "year", "time",
            name="uq_movie_name_year_time"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    uuid: Mapped[python_uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        default=python_uuid.uuid4,
        unique=True,
        nullable=False,
        index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    time: Mapped[int] = mapped_column(Integer, nullable=False)
    imdb: Mapped[float] = mapped_column(Float, nullable=False)
    votes: Mapped[int] = mapped_column(Integer, nullable=False)
    meta_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    gross: Mapped[float | None] = mapped_column(Float, nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    price: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    certification_id: Mapped[int] = mapped_column(
        ForeignKey("certifications.id"),
        nullable=False
    )

    certification: Mapped["Certification"] = relationship(
        back_populates="movies"
    )

    genres: Mapped[list["Genre"]] = relationship(
        secondary=movie_genres,
        back_populates="movies"
    )

    stars: Mapped[list["Star"]] = relationship(
        secondary=movie_stars,
        back_populates="movies"
    )

    directors: Mapped[list["Director"]] = relationship(
        secondary=movie_directors,
        back_populates="movies"
    )

    favorited_by: Mapped[list["User"]] = relationship(
        secondary=favorite_movies,
        back_populates="favorite_movies"
    )
