DROP TABLE IF EXISTS TAGGINGS;
DROP TABLE IF EXISTS OBJECTS;
DROP TABLE IF EXISTS DIMENSIONS;
DROP TABLE IF EXISTS BLOB;
DROP TABLE IF EXISTS TAGS;
DROP TABLE IF EXISTS PLUGINS;
DROP TABLE IF EXISTS CONCEPTS;


CREATE TABLE PLUGINS (
  ID BIGSERIAL PRIMARY KEY NOT NULL,
  NAME VARCHAR(128) NOT NULL UNIQUE,
  MODULE VARCHAR(128) NOT NULL UNIQUE
);

CREATE TABLE CONCEPTS (
    ID BIGSERIAL PRIMARY KEY NOT NULL,
    TITLE VARCHAR(128) NOT NULL UNIQUE,
    DESCRIPTION TEXT NOT NULL DEFAULT ''
);

CREATE TABLE TAGS (
  ID BIGSERIAL PRIMARY KEY NOT NULL,
  VALUE VARCHAR(128) NOT NULL,
  DESCRIPTION VARCHAR(128) DEFAULT '' NOT NULL,
  MUTABLE BOOL DEFAULT TRUE NOT NULL,
  TYPE BIGINT NOT NULL,
  CONCEPT_ID BIGINT NULL,
  PLUGIN_ID BIGINT NULL,
  FOREIGN KEY(CONCEPT_ID) REFERENCES CONCEPTS(ID),
  FOREIGN KEY(PLUGIN_ID) REFERENCES PLUGINS(ID)
);

CREATE TABLE OBJECTS (
  ID BIGSERIAL PRIMARY KEY NOT NULL,
  NAME VARCHAR(128) NOT NULL,
  DIGEST VARCHAR(128) NOT NULL,
  CONSTRAINT OBJECTS_UNIQUE_NAME_DIGEST UNIQUE (NAME, DIGEST)
);

CREATE TABLE DIMENSIONS (
  ROOT_TAG_ID BIGINT NOT NULL,
  NODE_TAG_ID BIGINT NOT NULL,
  LEFT_BORDER BIGINT NOT NULL,
  RIGHT_BORDER BIGINT NOT NULL,
  CONSTRAINT DIMENSIONS_PK PRIMARY KEY(ROOT_TAG_ID, NODE_TAG_ID),
  FOREIGN KEY(ROOT_TAG_ID) REFERENCES TAGS(ID),
  FOREIGN KEY(NODE_TAG_ID) REFERENCES TAGS(ID)
);

CREATE TABLE TAGGINGS (
  ID BIGSERIAL PRIMARY KEY NOT NULL,
  OBJECT_ID BIGINT NOT NULL,
  TAG_ID BIGINT NOT NULL,
  PLUGIN_ID BIGINT NULL,
  PLUGIN_SET_ID BIGINT NULL,
  META VARCHAR(128),
  FOREIGN KEY(TAG_ID) REFERENCES TAGS(ID),
  FOREIGN KEY(OBJECT_ID) REFERENCES OBJECTS(ID),
  FOREIGN KEY(PLUGIN_ID) REFERENCES PLUGINS(ID)
);
