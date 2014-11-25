-- Create Database
create database remote:localhost/NetworkLabs2 root root plocal
connect remote:localhost/NetworkLabs2 root root

-- Create Vertices

-- Create Person
create class Person extends V
create property Person.first_name string
create property Person.last_name string
create property Person.age integer
create property Person.cuisines_liked embeddedlist string
create property Person.dollar_limit float
create property Person.email string
alter property Person.email mandatory true 
create property Person.ethnicity string
create property Person.gender string
create property Person.is_vegetarian boolean
create property Person.last_request_time datetime 
create property Person.prob_of_activity float
create property Person.prob_of_comment float
create property Person.prob_of_like float
create property Person.year string
create property Person.major string

-- Create Card
create class Card extends V
create property Card.comment_count integer
create property Card.comment_count comment_list embeddedlist embeddedmap
create property Card.created_at datetime
create property Card.created_by link Person
create property Card.like_count integer
create property Card.like_list string
create property Card.comment_count string
create property Card.comment_count string
create property Card.comment_count string
create property Card.comment_count string
create property Card.comment_count string
create property Card.comment_count string
create property Card.comment_count string
create property Card.comment_count string
create property Card.comment_count string

-- Drop Database
-- drop database plocal:localhost/networklabs2 root root