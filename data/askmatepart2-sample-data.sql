--
-- PostgreSQL database dump
--

-- Dumped from database version 9.5.6
-- Dumped by pg_dump version 9.5.6

ALTER TABLE IF EXISTS ONLY public.question
    DROP CONSTRAINT IF EXISTS pk_question_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.answer
    DROP CONSTRAINT IF EXISTS pk_answer_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.answer
    DROP CONSTRAINT IF EXISTS fk_question_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.comment
    DROP CONSTRAINT IF EXISTS pk_comment_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.comment
    DROP CONSTRAINT IF EXISTS fk_comment_question_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.comment
    DROP CONSTRAINT IF EXISTS fk_answer_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.question_tag
    DROP CONSTRAINT IF EXISTS pk_question_tag_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.question_tag
    DROP CONSTRAINT IF EXISTS fk_question_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.tag
    DROP CONSTRAINT IF EXISTS pk_tag_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.question_tag
    DROP CONSTRAINT IF EXISTS fk_tag_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.users
    DROP CONSTRAINT IF EXISTS pk_user_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.answer
    DROP CONSTRAINT IF EXISTS fk_answer_user_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.comment
    DROP CONSTRAINT IF EXISTS fk_comment_user_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.question
    DROP CONSTRAINT IF EXISTS fk_question_user_id CASCADE;


DROP TABLE IF EXISTS public.question;
CREATE TABLE question
(
    id              serial                      NOT NULL,
    user_id         integer                     NOT NULL,
    submission_time TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT date_trunc('second', now()),
    view_number     integer                              DEFAULT 0,
    vote_number     integer                              DEFAULT 0,
    title           text,
    message         text,
    image           text
);

DROP TABLE IF EXISTS public.answer;
CREATE TABLE answer
(
    id              serial                      NOT NULL,
    user_id         integer                     NOT NULL,
    question_id     integer,
    submission_time TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT date_trunc('second', now()),
    vote_number     integer                              DEFAULT 0,
    message         text,
    image           text,
    accepted        boolean                     NOT NULL DEFAULT false
);

DROP TABLE IF EXISTS public.comment;
CREATE TABLE comment
(
    id              serial                      NOT NULL,
    user_id         integer,
    question_id     integer,
    answer_id       integer,
    message         text,
    submission_time TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT date_trunc('second', now()),
    edited_count    integer                              default 0
);


DROP TABLE IF EXISTS public.question_tag;
CREATE TABLE question_tag
(
    question_id integer NOT NULL,
    tag_id      integer NOT NULL
);

DROP TABLE IF EXISTS public.tag;
CREATE TABLE tag
(
    id   serial NOT NULL,
    name text
);

DROP TABLE IF EXISTS public.users;
CREATE TABLE users
(
    user_id           serial                      NOT NULL,
    email             CHARACTER VARYING(255)      NOT NULL UNIQUE,
    hashed_password   CHARACTER VARYING(255)      NOT NULL,
    reputation        INTEGER                              DEFAULT 0,
    registration_time TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT date_trunc('second', now())
);


ALTER TABLE ONLY answer
    ADD CONSTRAINT pk_answer_id PRIMARY KEY (id);

ALTER TABLE ONLY comment
    ADD CONSTRAINT pk_comment_id PRIMARY KEY (id);

ALTER TABLE ONLY question
    ADD CONSTRAINT pk_question_id PRIMARY KEY (id);

ALTER TABLE ONLY question_tag
    ADD CONSTRAINT pk_question_tag_id PRIMARY KEY (question_id, tag_id);

ALTER TABLE ONLY tag
    ADD CONSTRAINT pk_tag_id PRIMARY KEY (id);

ALTER TABLE ONLY users
    ADD CONSTRAINT pk_user_id PRIMARY KEY (user_id);

ALTER TABLE ONLY comment
    ADD CONSTRAINT fk_answer_id FOREIGN KEY (answer_id) REFERENCES answer (id);

ALTER TABLE ONLY comment
    ADD CONSTRAINT fk_comment_user_id FOREIGN KEY (user_id) REFERENCES users (user_id);

ALTER TABLE ONLY answer
    ADD CONSTRAINT fk_question_id FOREIGN KEY (question_id) REFERENCES question (id);

ALTER TABLE ONLY answer
    ADD CONSTRAINT fk_answer_user_id FOREIGN KEY (user_id) REFERENCES users (user_id);

ALTER TABLE ONLY question_tag
    ADD CONSTRAINT fk_question_id FOREIGN KEY (question_id) REFERENCES question (id);

ALTER TABLE ONLY question
    ADD CONSTRAINT fk_question_user_id FOREIGN KEY (user_id) REFERENCES users (user_id);

ALTER TABLE ONLY comment
    ADD CONSTRAINT fk_comment_question_id FOREIGN KEY (question_id) REFERENCES question (id);

ALTER TABLE ONLY question_tag
    ADD CONSTRAINT fk_tag_id FOREIGN KEY (tag_id) REFERENCES tag (id);

INSERT INTO users
VALUES (0, 'omar@mail.com', '$2b$12$zpMJrqqIBq3lUC1zOyscLu..vdcil3jnKiZUMbWMZkxsAq57kgBLK', 0);
INSERT INTO users
VALUES (1, 'adam@mail.com', '$2b$12$VBF9IXpnHvXUKHeci8dldeYdKD7KOyo4ZeQQeaBJWF9ocIIxD2976', 0);
INSERT INTO users
VALUES (2, 'eni@mail.com', '$2b$12$I.Lcsl4d/MBoaA0TeMtePex2/7Y.LKhHMhFU3GXnOw5sX3cHk9.SG', 0);


INSERT INTO question
VALUES (0, 1, '2017-04-28 08:29:00', 29, 7, 'How to make lists in Python?', 'I am totally new to this, any hints?',
        NULL);
INSERT INTO question
VALUES (1, 2, '2017-04-29 09:19:00', 15, 9, 'Wordpress loading multiple jQuery Versions', 'I developed a plugin that uses the jquery booklet plugin (http://builtbywill.com/booklet/#/) this plugin binds a function to $ so I cann call $(".myBook").booklet();

I could easy managing the loading order with wp_enqueue_script so first I load jquery then I load booklet so everything is fine.

BUT in my theme i also using jquery via webpack so the loading order is now following:

jquery
booklet
app.js (bundled file with webpack, including jquery)', 'images/image1.png');
INSERT INTO question
VALUES (2, 1, '2017-05-01 10:41:00', 1364, 57, 'Drawing canvas with an image picked with Cordova Camera Plugin', 'I''m getting an image from device and drawing a canvas with filters using Pixi JS. It works all well using computer to get an image. But when I''m on IOS, it throws errors such as cross origin issue, or that I''m trying to use an unknown format.
', NULL);

INSERT INTO question
VALUES (3, 0, '2019-04-28 10:29:00', 0, 0, 'list/array vs set',
        'What is the difference between a list/array and a set?',
        NULL);

INSERT INTO question
VALUES (4, 0, '2015-04-28 13:29:00', 0, 0, 'sorting', 'What do we call an *in-place* sort?',
        NULL);

INSERT INTO question
VALUES (5, 0, '2016-04-08 10:45:00', 0, 0, 'call stack', 'What is the call stack?',
        NULL);

INSERT INTO question
VALUES (6, 2, '2020-02-28 11:29:00', 0, 0, 'Stack Overflow', 'What is “Stack overflow”?',
        NULL);

INSERT INTO question
VALUES (7, 2, '2018-04-22 10:29:00', 0, 0, 'immutable??!!', 'What does it mean that an object is immutable in Python?',
        NULL);

INSERT INTO question
VALUES (8, 2, '2019-03-21 10:29:00', 0, 0, 'conditional expressions', 'What is conditional expression in Python?',
        NULL);

INSERT INTO question
VALUES (9, 2, '2014-01-28 10:59:00', 0, 0, 'shadowing', 'What is variable shadowing? ',
        NULL);

INSERT INTO question
VALUES (10, 2, '2019-12-24 10:29:00', 0, 0, 'Batman vs Superman', 'Who would win? Batman or Superman?',
        NULL);

SELECT pg_catalog.setval('question_id_seq', 10, true);

INSERT INTO answer
VALUES (1, 1, 1, '2017-04-28 16:49:00', 4, 'You need to use brackets: my_list = []', NULL, false);

INSERT INTO answer
VALUES (2, 2, 1, '2017-04-25 14:42:00', 35, 'Look it up in the Python docs', 'images/image2.jpg', false);

INSERT INTO answer
VALUES (3, 1, 3, '2019-04-28 16:49:00', 4,
        'lists are mutable, ordered, changeble objects. Set are unordered, unindexed, non mutable', NULL, false);

INSERT INTO answer
VALUES (4, 1, 4, '2015-04-28 16:55:00', 4, 'Modifies the mutable objects where it is declared. No need new variable.
list.sort() -> [1, 2, 3, 4]', NULL, false);

INSERT INTO answer
VALUES (5, 1, 5, '2016-04-09 16:55:00', 4, 'A call stack is a buffer that stores requests, that need to be handled.
A stack contains information about a function: name, parameter, execution.', NULL, false);

INSERT INTO answer
VALUES (6, 1, 6, '2020-03-01 16:55:00', 4, 'It is a runtime error when the software or hadrware runs out of memory limit.
It usually happens with recursive functions without a breaking point.', NULL, false);

INSERT INTO answer
VALUES (7, 1, 7, '2018-04-25 16:55:00', 4, 'We can not change the object''s value. We can only assign with a new one.
boolean, int, float, string, tuple.', NULL, false);

INSERT INTO answer
VALUES (8, 1, 8, '2019-03-25 16:55:00', 4, 'if the headline is True, the statements runs.
An expression what we created.
If, elif, else. ', NULL, false);

INSERT INTO answer
VALUES (9, 1, 9, '2014-02-01 16:55:00', 4,
        'when a variable declared within a certain scope has the same name as a variable declared in an outer scope.',
        NULL, false);

INSERT INTO answer
VALUES (10, 1, 10, '2019-12-25 16:55:00', 4, 'are you sure you are in the good topic for this question? :)', NULL,
        false);

SELECT pg_catalog.setval('answer_id_seq', 10, true);

INSERT INTO comment
VALUES (1, 2, 0, NULL, 'Please clarify the question as it is too vague!', '2017-05-01 05:49:00');
INSERT INTO comment
VALUES (2, 1, NULL, 1, 'I think you could use my_list = list() as well.', '2017-05-02 16:55:00');
SELECT pg_catalog.setval('comment_id_seq', 2, true);

INSERT INTO tag
VALUES (1, 'python');
INSERT INTO tag
VALUES (2, 'sql');
INSERT INTO tag
VALUES (3, 'css');
SELECT pg_catalog.setval('tag_id_seq', 3, true);

INSERT INTO question_tag
VALUES (0, 1);
INSERT INTO question_tag
VALUES (1, 3);
INSERT INTO question_tag
VALUES (2, 3);

