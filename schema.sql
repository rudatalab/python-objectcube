drop table if exists TAG;
drop table if exists CONCEPTS;
drop table if exists CONCEPT_TYPE;

CREATE TABLE CONCEPT_TYPE (
	id SERIAL primary key not null,
	name varchar(128) UNIQUE not null,
	regex_pattern varchar(128) null,
	concept_base_type varchar(14) not null default 'ALPHANUMERICAL',

    CONSTRAINT chk_concept_base_type CHECK (concept_base_type IN (
                                       'DATE',
                                       'TIME',
                                       'DATETIME',
                                       'ALPHANUMERICAL',
                                       'NUMERICAL',
                                       'REGEX')
    )
);

CREATE TABLE CONCEPTS (
	id SERIAL primary key not null,
	name varchar(128) UNIQUE not null,
	description varchar(128) not null default '',
	concept_type_id INT NOT NULL,
	constraint FK_concept_type 
	foreign key(concept_type_id) references CONCEPT_TYPE(id)
);

CREATE TABLE TAG (
	id SERIAL primary key not null,
	name varchar(128) not null,
	description varchar(128) not null default '',
	concepts_id INT NOT NULL,
	concept_type_id INT not null,
	constraint FK_concepts
	foreign key(concepts_id) references CONCEPTS(id),
	foreign key(concept_type_id) references CONCEPT_TYPE(id)
);
