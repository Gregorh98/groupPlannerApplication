CREATE TABLE groupPlanner.entries (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    date date NOT NULL,
    available boolean DEFAULT false NOT NULL
);

CREATE TABLE groupPlanner.users (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name character varying NOT NULL,
    group_code character varying NOT NULL
);


ALTER TABLE ONLY groupPlanner.entries
    ADD CONSTRAINT entries_pk PRIMARY KEY (id);

ALTER TABLE ONLY groupPlanner.users
    ADD CONSTRAINT users_pk PRIMARY KEY (id);

