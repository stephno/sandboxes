---------------------
-- Try It Yourself --
---------------------

-- 1 --
CREATE TABLE albums (
  album_id bigserial,
  album_catalogue_code varchar(100) NOT NULL,
  album_title text NOT NULL,
  album_artist text NOT NULL,
  album_release_date date NOT NULL,
  album_genre varchar(40),
  album_description text
  CONSTRAINT album_key PRIMARY KEY (album_id)
);

CREATE TABLE songs (
  song_id bigserial,
  song_title text NOT NULL,
  song_artist text NOT NULL,
  album_id bigint REFERENCES albums (album_id)
);


-- 2 --
-- The title and artist columns from both tables should get
-- short enough content so that we could only use a varchar type.
-- Then the album_catalogue_code column could be used
-- as a natural key, at least as long as two publishers do not use
-- the same catalogue code… Hence the album_id column my not have
-- been a bad idea (+ the integer type should speed up queries).
CREATE TABLE albums (
  album_catalogue_code varchar(100) CONSTRAINT album_key PRIMARY KEY,
  album_title varchar(200) NOT NULL,
  album_artist varchar(300) NOT NULL,
  album_release_date date NOT NULL,
  album_genre varchar(40),
  album_description text
);

CREATE TABLE songs (
  song_id bigserial,
  song_title varchar(200) NOT NULL,
  song_artist varchar(300) NOT NULL,
  album_catalogue_code bigint REFERENCES albums (album_catalogue_code)
);
