# Where the runs disagree: dev_zero_shot vs dev_qlora_r16_final

1034 questions compared. Fixed: 61. Broken: 47.

Cases in each section are in random order (seed 0), so the first ten are a fair sample.

## Auto tag counts

| Tag | Fixed | Broken |
|---|---|---|
| T1/T2 aliases added | 8 | 11 |
| joins 1->2 | 15 | 3 |
| no longer runs | 0 | 17 |
| now runs | 15 | 0 |
| SELECTs 1->2 (subqueries/set ops) | 11 | 3 |
| joins 0->1 | 4 | 9 |
| T1/T2 aliases removed | 10 | 2 |
| DISTINCT removed | 10 | 2 |
| joins 1->0 | 9 | 2 |
| SELECTs 2->1 (subqueries/set ops) | 1 | 5 |
| SELECTs 3->2 (subqueries/set ops) | 0 | 3 |
| DISTINCT added | 3 | 0 |
| joins 2->1 | 2 | 1 |
| GROUP BY added | 1 | 1 |
| joins 0->2 | 0 | 2 |
| joins 3->2 | 0 | 2 |
| joins 1->3 | 2 | 0 |
| SELECTs 2->3 (subqueries/set ops) | 0 | 2 |
| GROUP BY removed | 1 | 1 |
| HAVING added | 1 | 0 |
| joins 2->3 | 0 | 1 |

## Fixed: wrong in dev_zero_shot, right in dev_qlora_r16_final

### 1. `cre_Doc_Template_Mgt` (question #312)

**Question:** Return the id and type code of the template that is used for the greatest number of documents.

**Gold:**
```sql
SELECT T1.template_id ,  T2.Template_Type_Code FROM Documents AS T1 JOIN Templates AS T2 ON T1.template_id  =  T2.template_id GROUP BY T1.template_id ORDER BY count(*) DESC LIMIT 1
```

**dev_zero_shot:**
```sql
SELECT T1.Template_ID, T1.Template_Type_Code FROM Templates AS T1 JOIN Documents AS T2 ON T1.Template_ID = T2.Template_ID GROUP BY T1.Template_ID, T1.Template_Type_Code ORDER BY COUNT(T2.Document_ID) DESC LIMIT 1
```

**dev_qlora_r16_final:**
```sql
SELECT T1.template_id ,  T1.template_type_code FROM Templates AS T1 JOIN Documents AS T2 ON T1.template_id  =  T2.template_id GROUP BY T1.template_id ORDER BY count(*) DESC LIMIT 1
```

**Auto tags:** none

**Category:** 
 fixed incorrect group by
### 2. `student_transcripts_tracking` (question #534)

**Question:** What are the first, middle, and last names, along with the ids, of all students who enrolled in 2 degree programs in one semester?

**Gold:**
```sql
SELECT T1.first_name ,  T1.middle_name ,  T1.last_name ,  T1.student_id FROM Students AS T1 JOIN Student_Enrolment AS T2 ON T1.student_id  =  T2.student_id GROUP BY T1.student_id HAVING count(*)  =  2
```

**dev_zero_shot:**
```sql
SELECT T1.first_name, T1.middle_name, T1.last_name, T1.student_id FROM Students AS T1 JOIN Student_Enrolment AS T2 ON T1.student_id = T2.student_id GROUP BY T1.student_id HAVING COUNT(DISTINCT T2.degree_program_id) = 2
```

**dev_qlora_r16_final:**
```sql
SELECT T1.first_name ,  T1.middle_name ,  T1.last_name ,  T1.student_id FROM Students AS T1 JOIN Student_Enrolment AS T2 ON T1.student_id  =  T2.student_id GROUP BY T1.student_id HAVING count(*)  =  2
```

**Auto tags:** DISTINCT removed

**Category:** 
 removed disctinct in having
### 3. `battle_death` (question #504)

**Question:** List the name and date the battle that has lost the ship named 'Lettice' and the ship named 'HMS Atalanta'

**Gold:**
```sql
SELECT T1.name ,  T1.date FROM battle AS T1 JOIN ship AS T2 ON T1.id  =  T2.lost_in_battle WHERE T2.name  =  'Lettice' INTERSECT SELECT T1.name ,  T1.date FROM battle AS T1 JOIN ship AS T2 ON T1.id  =  T2.lost_in_battle WHERE T2.name  =  'HMS Atalanta'
```

**dev_zero_shot:**
```sql
SELECT T1.name, T1.date FROM battle AS T1 JOIN ship AS T2 ON T1.id = T2.lost_in_battle WHERE T2.name IN ('Lettice', 'HMS Atalanta')
```

**dev_qlora_r16_final:**
```sql
SELECT T1.name ,  T1.date FROM battle AS T1 JOIN ship AS T2 ON T1.id  =  T2.lost_in_battle WHERE T2.name  =  'Lettice' INTERSECT SELECT T1.name ,  T1.date FROM battle AS T1 JOIN ship AS T2 ON T1.id  =  T2.lost_in_battle WHERE T2.name  =  'HMS Atalanta'
```

**Auto tags:** joins 1->2, SELECTs 1->2 (subqueries/set ops)

**Category:** 
 added intersect and following select
### 4. `tvshow` (question #637)

**Question:** Find the series name and country of the tv channel that is playing some cartoons directed by Ben Jones and Michael Chang?

**Gold:**
```sql
SELECT T1.series_name ,  T1.country FROM TV_Channel AS T1 JOIN cartoon AS T2 ON T1.id = T2.Channel WHERE T2.directed_by  =  'Michael Chang' INTERSECT SELECT T1.series_name ,  T1.country FROM TV_Channel AS T1 JOIN cartoon AS T2 ON T1.id = T2.Channel WHERE T2.directed_by  =  'Ben Jones'
```

**dev_zero_shot:**
```sql
SELECT T1.series_name, T1.Country FROM TV_Channel AS T1 JOIN Cartoon AS T2 ON T1.id = T2.Channel WHERE T2.Directed_by IN ('Ben Jones', 'Michael Chang')
```

**dev_qlora_r16_final:**
```sql
SELECT t1.series_name ,  t1.country FROM TV_channel AS t1 JOIN cartoon AS t2 ON t1.id  =  t2.channel WHERE t2.directed_by  =  "Ben Jones" INTERSECT SELECT t1.series_name ,  t1.country FROM TV_channel AS t1 JOIN cartoon AS t2 ON t1.id  =  t2.channel WHERE t2.directed_by  =  "Michael Chang"
```

**Auto tags:** joins 1->2, SELECTs 1->2 (subqueries/set ops)

**Category:** 
added  intersect and following select
### 5. `world_1` (question #803)

**Question:** Return the names of the 3 most populated countries.

**Gold:**
```sql
SELECT Name FROM country ORDER BY Population DESC LIMIT 3
```

**dev_zero_shot:**
```sql
SELECT Name FROM city GROUP BY CountryCode ORDER BY SUM(Population) DESC LIMIT 3
```

**dev_qlora_r16_final:**
```sql
SELECT Name FROM country ORDER BY Population DESC LIMIT 3
```

**Auto tags:** GROUP BY removed

**Category:** 
 removed group by and fixed order by
### 6. `world_1` (question #754)

**Question:** What are the countries where either English or Dutch is the official language ?

**Gold:**
```sql
select t1.name from country as t1 join countrylanguage as t2 on t1.code  =  t2.countrycode where t2.language  =  "english" and isofficial  =  "t" union select t1.name from country as t1 join countrylanguage as t2 on t1.code  =  t2.countrycode where t2.language  =  "dutch" and isofficial  =  "t"
```

**dev_zero_shot:**
```sql
SELECT T1.Name FROM country AS T1 JOIN countrylanguage AS T2 ON T1.Code = T2.CountryCode WHERE T2.Language = 'English' OR T2.Language = 'Dutch'
```

**dev_qlora_r16_final:**
```sql
SELECT T1.Name FROM country AS T1 JOIN countrylanguage AS T2 ON T1.Code  =  T2.CountryCode WHERE T2.IsOfficial  =  'Yes' AND T2.Language  =  'English' UNION SELECT T1.Name FROM country AS T1 JOIN countrylanguage AS T2 ON T1.Code  =  T2.CountryCode WHERE T2.IsOfficial  =  'Yes' AND T2.Language  =  'Dutch'
```

**Auto tags:** joins 1->2, SELECTs 1->2 (subqueries/set ops)

**Category:** 
 added union and following select
### 7. `network_1` (question #891)

**Question:** Return the names of friends of the high school student Kyle.

**Gold:**
```sql
SELECT T3.name FROM Friend AS T1 JOIN Highschooler AS T2 ON T1.student_id  =  T2.id JOIN Highschooler AS T3 ON T1.friend_id  =  T3.id WHERE T2.name  =  "Kyle"
```

**dev_zero_shot:**
```sql
SELECT T2.name FROM Highschooler AS T1 JOIN Friend AS T2 ON T1.ID = T2.student_id WHERE T1.name = 'Kyle'
```

*Did not run:* `OperationalError: no such column: T2.name`

**dev_qlora_r16_final:**
```sql
SELECT T3.name FROM friend AS T1 JOIN highschooler AS T2 ON T1.student_id  =  T2.id JOIN highschooler AS T3 ON T1.friend_id  =  T3.id WHERE T2.name  =  'Kyle'
```

**Auto tags:** now runs, joins 1->2

**Category:** 
added missing join and selected from correct table
### 8. `car_1` (question #177)

**Question:** What are the id and names of the countries which have more than 3 car makers or produce the 'fiat' model?

**Gold:**
```sql
SELECT T1.countryId ,  T1.CountryName FROM Countries AS T1 JOIN CAR_MAKERS AS T2 ON T1.CountryId  =  T2.Country GROUP BY T1.countryId HAVING count(*)  >  3 UNION SELECT T1.countryId ,  T1.CountryName FROM Countries AS T1 JOIN CAR_MAKERS AS T2 ON T1.CountryId  =  T2.Country JOIN MODEL_LIST AS T3 ON T2.Id  =  T3.Maker WHERE T3.Model  =  'fiat';
```

**dev_zero_shot:**
```sql
SELECT T1.CountryId, T1.CountryName FROM countries AS T1 JOIN car_makers AS T2 ON T1.CountryId = T2.Country WHERE T2.Country = 'fiat' GROUP BY T1.CountryId HAVING COUNT(T2.Maker) > 3
```

**dev_qlora_r16_final:**
```sql
SELECT T1.Countryid ,  T1.CountryName FROM countries AS T1 JOIN car_makers AS T2 ON T1.Countryid  =  T2.Country GROUP BY T1.Countryid HAVING count(*)  >  3 UNION SELECT T1.Countryid ,  T1.CountryName FROM countries AS T1 JOIN car_makers AS T2 ON T1.Countryid  =  T2.Country JOIN model_list AS T3 ON T2.id  =  T3.Maker WHERE T3.Model  =  'fiat'
```

**Auto tags:** joins 1->3, SELECTs 1->2 (subqueries/set ops)

**Category:** 
 added missining union and following select
### 9. `flight_2` (question #183)

**Question:** List all airline names and their abbreviations in "USA".

**Gold:**
```sql
SELECT Airline ,  Abbreviation FROM AIRLINES WHERE Country  =  "USA"
```

**dev_zero_shot:**
```sql
SELECT T1.Airline, T1.Abbreviation FROM airlines AS T1 JOIN airports AS T2 ON T1.Country = T2.Country WHERE T2.Country = 'USA'
```

**dev_qlora_r16_final:**
```sql
SELECT Airline ,  Abbreviation FROM airlines WHERE Country  =  'USA'
```

**Auto tags:** joins 1->0, T1/T2 aliases removed

**Category:** 
removed uneccessary joins
### 10. `network_1` (question #908)

**Question:** Show the names of students who have at least 2 likes.

**Gold:**
```sql
SELECT T2.name FROM Likes AS T1 JOIN Highschooler AS T2 ON T1.student_id  =  T2.id GROUP BY T1.student_id HAVING count(*)  >=  2
```

**dev_zero_shot:**
```sql
SELECT T1.name FROM Highschooler AS T1 JOIN Likes AS T2 ON T1.ID  =  T2.student_id GROUP BY T1.name HAVING count(*)  >=  2
```

**dev_qlora_r16_final:**
```sql
SELECT T1.name FROM Highschooler AS T1 JOIN Likes AS T2 ON T1.id  =  T2.student_id GROUP BY T2.student_id HAVING count(*)  >=  2
```

**Auto tags:** none

**Category:** 
fixed group by
### 11. `dog_kennels` (question #957)

**Question:** Find the first names of owners living in Virginia and the names of dogs they own.

**Gold:**
```sql
SELECT T1.first_name ,  T2.name FROM Owners AS T1 JOIN Dogs AS T2 ON T1.owner_id  =  T2.owner_id WHERE T1.state  =  'Virginia'
```

**dev_zero_shot:**
```sql
SELECT DISTINCT O.first_name, D.name FROM Owners O JOIN Dogs D ON O.owner_id = D.owner_id WHERE O.state = 'VA'
```

**dev_qlora_r16_final:**
```sql
SELECT T1.first_name ,  T2.name FROM Owners AS T1 JOIN Dogs AS T2 ON T1.owner_id  =  T2.owner_id WHERE T1.state  =  "Virginia"
```

**Auto tags:** DISTINCT removed, T1/T2 aliases added

**Category:** 

### 12. `dog_kennels` (question #968)

**Question:** How many professionals have performed any treatment to dogs?

**Gold:**
```sql
SELECT count(DISTINCT professional_id) FROM Treatments
```

**dev_zero_shot:**
```sql
SELECT COUNT(professional_id) FROM Treatments
```

**dev_qlora_r16_final:**
```sql
SELECT count(DISTINCT professional_id) FROM treatments
```

**Auto tags:** DISTINCT added

**Category:** 

### 13. `course_teach` (question #403)

**Question:** Show the name of the teacher for the math course.

**Gold:**
```sql
SELECT T3.Name FROM course_arrange AS T1 JOIN course AS T2 ON T1.Course_ID  =  T2.Course_ID JOIN teacher AS T3 ON T1.Teacher_ID  =  T3.Teacher_ID WHERE T2.Course  =  "Math"
```

**dev_zero_shot:**
```sql
SELECT T2.Name FROM course AS T1 INNER JOIN teacher AS T2 ON T1.Course_ID = T2.Course_ID WHERE T1.Course = 'math'
```

*Did not run:* `OperationalError: no such column: T2.Course_ID`

**dev_qlora_r16_final:**
```sql
SELECT T3.Name FROM course_arrange AS T1 JOIN course AS T2 ON T1.Course_ID  =  T2.Course_ID JOIN teacher AS T3 ON T1.Teacher_ID  =  T3.Teacher_ID WHERE T2.Course  =  "Math"
```

**Auto tags:** now runs, joins 1->2

**Category:** 

### 14. `wta_1` (question #483)

**Question:** Find the name and rank of the 3 youngest winners across all matches.

**Gold:**
```sql
SELECT DISTINCT winner_name ,  winner_rank FROM matches ORDER BY winner_age LIMIT 3
```

**dev_zero_shot:**
```sql
SELECT T1.first_name, T1.last_name, T1.rank FROM players AS T1 JOIN matches AS T2 ON T1.player_id = T2.winner_id ORDER BY T2.winner_age ASC LIMIT 3
```

*Did not run:* `OperationalError: no such column: T1.rank`

**dev_qlora_r16_final:**
```sql
SELECT winner_name ,  winner_rank FROM matches ORDER BY winner_age ASC LIMIT 3
```

**Auto tags:** now runs, joins 1->0, T1/T2 aliases removed

**Category:** 

### 15. `wta_1` (question #484)

**Question:** What are the names and ranks of the three youngest winners across all matches?

**Gold:**
```sql
SELECT DISTINCT winner_name ,  winner_rank FROM matches ORDER BY winner_age LIMIT 3
```

**dev_zero_shot:**
```sql
SELECT T1.first_name, T1.last_name, T1.winner_rank FROM players AS T1 JOIN matches AS T2 ON T1.player_id = T2.winner_id ORDER BY T2.winner_age ASC LIMIT 3
```

*Did not run:* `OperationalError: no such column: T1.winner_rank`

**dev_qlora_r16_final:**
```sql
SELECT winner_name ,  winner_rank FROM matches ORDER BY winner_age ASC LIMIT 3
```

**Auto tags:** now runs, joins 1->0, T1/T2 aliases removed

**Category:** 

### 16. `dog_kennels` (question #943)

**Question:** Find the id and cell phone of the professionals who operate two or more types of treatments.

**Gold:**
```sql
SELECT T1.professional_id ,  T1.cell_number FROM Professionals AS T1 JOIN Treatments AS T2 ON T1.professional_id  =  T2.professional_id GROUP BY T1.professional_id HAVING count(*)  >=  2
```

**dev_zero_shot:**
```sql
SELECT professional_id, cell_number FROM Treatments GROUP BY professional_id HAVING COUNT(DISTINCT treatment_type_code) >= 2
```

*Did not run:* `OperationalError: no such column: cell_number`

**dev_qlora_r16_final:**
```sql
SELECT T1.professional_id ,  T1.cell_number FROM Professionals AS T1 JOIN Treatments AS T2 ON T1.professional_id  =  T2.professional_id GROUP BY T1.professional_id HAVING count(*)  >=  2
```

**Auto tags:** now runs, joins 0->1, DISTINCT removed, T1/T2 aliases added

**Category:** 

### 17. `concert_singer` (question #37)

**Question:** List all singer names in concerts in year 2014.

**Gold:**
```sql
SELECT T2.name FROM singer_in_concert AS T1 JOIN singer AS T2 ON T1.singer_id  =  T2.singer_id JOIN concert AS T3 ON T1.concert_id  =  T3.concert_id WHERE T3.year  =  2014
```

**dev_zero_shot:**
```sql
SELECT T2.Name FROM concert AS T1 INNER JOIN singer AS T2 ON T1.concert_ID = T2.Singer_ID WHERE T1.Year = '2014'
```

**dev_qlora_r16_final:**
```sql
SELECT T3.Name FROM concert AS T1 JOIN singer_in_concert AS T2 ON T1.concert_ID  =  T2.concert_ID JOIN singer AS T3 ON T2.Singer_ID  =  T3.Singer_ID WHERE T1.Year  =  2014
```

**Auto tags:** joins 1->2

**Category:** 

### 18. `pets_1` (question #75)

**Question:** Find the first name and age of students who have a pet.

**Gold:**
```sql
SELECT DISTINCT T1.fname ,  T1.age FROM student AS T1 JOIN has_pet AS T2 ON T1.stuid  =  T2.stuid
```

**dev_zero_shot:**
```sql
SELECT T1.Fname, T1.Age FROM Student AS T1 JOIN Has_Pet AS T2 ON T1.StuID = T2.StuID
```

**dev_qlora_r16_final:**
```sql
SELECT DISTINCT T1.fname ,  T1.age FROM Student AS T1 JOIN Has_Pet AS T2 ON T1.StuID  =  T2.StuID
```

**Auto tags:** DISTINCT added

**Category:** 

### 19. `world_1` (question #724)

**Question:** What is the average life expectancy in African countries that are republics?

**Gold:**
```sql
SELECT avg(LifeExpectancy) FROM country WHERE Continent  =  "Africa" AND GovernmentForm  =  "Republic"
```

**dev_zero_shot:**
```sql
SELECT AVG(T1.LifeExpectancy) FROM country AS T1 INNER JOIN countrylanguage AS T2 ON T1.Code = T2.CountryCode WHERE T1.Continent = 'Africa' AND T1.GovernmentForm = 'Republic'
```

**dev_qlora_r16_final:**
```sql
SELECT avg(LifeExpectancy) FROM country WHERE Continent  =  'Africa' AND GovernmentForm  =  'Republic'
```

**Auto tags:** joins 1->0, T1/T2 aliases removed

**Category:** 

### 20. `world_1` (question #709)

**Question:** What is the continent name which Anguilla belongs to?

**Gold:**
```sql
SELECT Continent FROM country WHERE Name  =  "Anguilla"
```

**dev_zero_shot:**
```sql
SELECT T1.Continent FROM country AS T1 INNER JOIN city AS T2 ON T1.Code = T2.CountryCode WHERE T2.Name = 'Anguilla'
```

**dev_qlora_r16_final:**
```sql
SELECT Continent FROM country WHERE Name  =  'Anguilla'
```

**Auto tags:** joins 1->0, T1/T2 aliases removed

**Category:** 

### 21. `cre_Doc_Template_Mgt` (question #342)

**Question:** What are the different template type codes, and how many documents use each type?

**Gold:**
```sql
SELECT T1.template_type_code ,  count(*) FROM Templates AS T1 JOIN Documents AS T2 ON T1.template_id  =  T2.template_id GROUP BY T1.template_type_code
```

**dev_zero_shot:**
```sql
SELECT T1.Template_Type_Code, COUNT(DISTINCT T2.Document_ID) AS Document_Count FROM Ref_Template_Types AS T1 INNER JOIN Templates AS T2 ON T1.Template_Type_Code = T2.Template_Type_Code GROUP BY T1.Template_Type_Code
```

*Did not run:* `OperationalError: no such column: T2.Document_ID`

**dev_qlora_r16_final:**
```sql
SELECT T1.template_type_code ,  count(*) FROM Templates AS T1 JOIN Documents AS T2 ON T1.template_id  =  T2.template_id GROUP BY T1.template_type_code
```

**Auto tags:** now runs, DISTINCT removed

**Category:** 

### 22. `cre_Doc_Template_Mgt` (question #344)

**Question:** Return the code of the template type that is most commonly used in documents.

**Gold:**
```sql
SELECT T1.template_type_code FROM Templates AS T1 JOIN Documents AS T2 ON T1.template_id  =  T2.template_id GROUP BY T1.template_type_code ORDER BY count(*) DESC LIMIT 1
```

**dev_zero_shot:**
```sql
SELECT Template_Type_Code FROM Templates WHERE Template_ID IN (SELECT Template_ID FROM Documents GROUP BY Template_ID ORDER BY COUNT(*) DESC LIMIT 1)
```

**dev_qlora_r16_final:**
```sql
SELECT template_type_code FROM documents AS T1 JOIN templates AS T2 ON T1.template_id  =  T2.template_id GROUP BY template_type_code ORDER BY count(*) DESC LIMIT 1
```

**Auto tags:** joins 0->1, SELECTs 2->1 (subqueries/set ops), T1/T2 aliases added

**Category:** 

### 23. `network_1` (question #909)

**Question:** What are the names of students who have 2 or more likes?

**Gold:**
```sql
SELECT T2.name FROM Likes AS T1 JOIN Highschooler AS T2 ON T1.student_id  =  T2.id GROUP BY T1.student_id HAVING count(*)  >=  2
```

**dev_zero_shot:**
```sql
SELECT T1.name FROM Highschooler AS T1 JOIN Likes AS T2 ON T1.ID  =  T2.student_id GROUP BY T1.name HAVING count(*)  >=  2
```

**dev_qlora_r16_final:**
```sql
SELECT T1.name FROM Highschooler AS T1 JOIN Likes AS T2 ON T1.id  =  T2.student_id GROUP BY T2.student_id HAVING count(*)  >=  2
```

**Auto tags:** none

**Category:** 

### 24. `network_1` (question #887)

**Question:** Return the name of the high school student with the most friends.

**Gold:**
```sql
SELECT T2.name FROM Friend AS T1 JOIN Highschooler AS T2 ON T1.student_id  =  T2.id GROUP BY T1.student_id ORDER BY count(*) DESC LIMIT 1
```

**dev_zero_shot:**
```sql
SELECT T1.name FROM Highschooler AS T1 JOIN Friend AS T2 ON T1.ID  =  T2.student_id GROUP BY T1.name ORDER BY count(*) DESC LIMIT 1
```

**dev_qlora_r16_final:**
```sql
SELECT T1.name FROM Highschooler AS T1 JOIN Friend AS T2 ON T1.id  =  T2.student_id GROUP BY T2.student_id ORDER BY count(*) DESC LIMIT 1
```

**Auto tags:** none

**Category:** 

### 25. `course_teach` (question #400)

**Question:** What is the name of each teacher and what course they teach?

**Gold:**
```sql
SELECT T3.Name ,  T2.Course FROM course_arrange AS T1 JOIN course AS T2 ON T1.Course_ID  =  T2.Course_ID JOIN teacher AS T3 ON T1.Teacher_ID  =  T3.Teacher_ID
```

**dev_zero_shot:**
```sql
SELECT T2.Name, T1.Course FROM course AS T1 JOIN course_arrange AS T2 ON T1.Course_ID = T2.Course_ID JOIN teacher AS T3 ON T2.Teacher_ID = T3.Teacher_ID
```

*Did not run:* `OperationalError: no such column: T2.Name`

**dev_qlora_r16_final:**
```sql
SELECT T1.Name ,  T3.Course FROM teacher AS T1 JOIN course_arrange AS T2 ON T1.Teacher_ID  =  T2.Teacher_ID JOIN course AS T3 ON T2.Course_ID  =  T3.Course_ID
```

**Auto tags:** now runs

**Category:** 

### 26. `tvshow` (question #636)

**Question:** What are the countries that are not playing cartoons written by Todd Casey?

**Gold:**
```sql
SELECT country FROM TV_Channel EXCEPT SELECT T1.country FROM TV_Channel AS T1 JOIN cartoon AS T2 ON T1.id = T2.Channel WHERE T2.written_by  =  'Todd Casey'
```

**dev_zero_shot:**
```sql
SELECT DISTINCT Country FROM TV_Channel WHERE id NOT IN ( SELECT Channel FROM Cartoon WHERE Written_by = 'Todd Casey' )
```

**dev_qlora_r16_final:**
```sql
SELECT country FROM TV_channel EXCEPT SELECT t2.country FROM cartoon AS t1 JOIN TV_channel AS t2 ON t1.channel  =  t2.id WHERE t1.written_by  =  "Todd Casey"
```

**Auto tags:** joins 0->1, DISTINCT removed, T1/T2 aliases added

**Category:** 

### 27. `cre_Doc_Template_Mgt` (question #308)

**Question:** Count the number of documents that use the PPT template type.

**Gold:**
```sql
SELECT count(*) FROM Documents AS T1 JOIN Templates AS T2 ON T1.Template_ID  =  T2.Template_ID WHERE T2.Template_Type_Code  =  'PPT'
```

**dev_zero_shot:**
```sql
SELECT COUNT(DISTINCT D.Document_ID) FROM Documents D JOIN Templates T ON D.Template_ID = T.Template_ID JOIN Ref_Template_Types R ON T.Template_Type_Code = R.Template_Type_Code WHERE R.Template_Type_Description = 'PPT'
```

**dev_qlora_r16_final:**
```sql
SELECT count(*) FROM documents AS T1 JOIN templates AS T2 ON T1.template_id  =  T2.template_id WHERE T2.template_type_code  =  "PPT"
```

**Auto tags:** joins 2->1, DISTINCT removed, T1/T2 aliases added

**Category:** 

### 28. `network_1` (question #886)

**Question:** What is the name of the high schooler who has the greatest number of friends?

**Gold:**
```sql
SELECT T2.name FROM Friend AS T1 JOIN Highschooler AS T2 ON T1.student_id  =  T2.id GROUP BY T1.student_id ORDER BY count(*) DESC LIMIT 1
```

**dev_zero_shot:**
```sql
SELECT T1.name FROM Highschooler AS T1 JOIN Friend AS T2 ON T1.ID  =  T2.student_id GROUP BY T1.name ORDER BY count(*) DESC LIMIT 1
```

**dev_qlora_r16_final:**
```sql
SELECT T1.name FROM Highschooler AS T1 JOIN Friend AS T2 ON T1.id  =  T2.student_id GROUP BY T2.student_id ORDER BY count(*) DESC LIMIT 1
```

**Auto tags:** none

**Category:** 

### 29. `cre_Doc_Template_Mgt` (question #311)

**Question:** What is the id and type code for the template used by the most documents?

**Gold:**
```sql
SELECT T1.template_id ,  T2.Template_Type_Code FROM Documents AS T1 JOIN Templates AS T2 ON T1.template_id  =  T2.template_id GROUP BY T1.template_id ORDER BY count(*) DESC LIMIT 1
```

**dev_zero_shot:**
```sql
SELECT T1.Template_ID, T1.Template_Type_Code FROM Templates AS T1 JOIN Documents AS T2 ON T1.Template_ID = T2.Template_ID GROUP BY T1.Template_ID, T1.Template_Type_Code ORDER BY COUNT(T2.Document_ID) DESC LIMIT 1
```

**dev_qlora_r16_final:**
```sql
SELECT T1.template_id ,  T1.template_type_code FROM Templates AS T1 JOIN Documents AS T2 ON T1.template_id  =  T2.template_id GROUP BY T1.template_id ORDER BY count(*) DESC LIMIT 1
```

**Auto tags:** none

**Category:** 

### 30. `car_1` (question #110)

**Question:** What is the number of car models that are produced by each maker and what is the id and full name of each maker?

**Gold:**
```sql
SELECT Count(*) ,  T2.FullName ,  T2.id FROM MODEL_LIST AS T1 JOIN CAR_MAKERS AS T2 ON T1.Maker  =  T2.Id GROUP BY T2.id;
```

**dev_zero_shot:**
```sql
SELECT T1.Maker, T1.Id, T1.FullName, COUNT(T2.Model) as ModelCount FROM car_makers AS T1 LEFT JOIN model_list AS T2 ON T1.Id = T2.Maker GROUP BY T1.Maker, T1.Id, T1.FullName
```

**dev_qlora_r16_final:**
```sql
SELECT count(*) ,  T1.id ,  T1.fullname FROM car_makers AS T1 JOIN model_list AS T2 ON T1.id  =  T2.Maker GROUP BY T1.id
```

**Auto tags:** none

**Category:** 

### 31. `cre_Doc_Template_Mgt` (question #379)

**Question:** Show the document id with paragraph text 'Brazil' and 'Ireland'.

**Gold:**
```sql
SELECT document_id FROM Paragraphs WHERE paragraph_text  =  'Brazil' INTERSECT SELECT document_id FROM Paragraphs WHERE paragraph_text  =  'Ireland'
```

**dev_zero_shot:**
```sql
SELECT T1.Document_ID FROM Paragraphs AS T1 WHERE T1.Paragraph_Text IN ('Brazil', 'Ireland')
```

**dev_qlora_r16_final:**
```sql
SELECT document_id FROM paragraphs WHERE paragraph_text  =  'Brazil' INTERSECT SELECT document_id FROM paragraphs WHERE paragraph_text  =  'Ireland'
```

**Auto tags:** SELECTs 1->2 (subqueries/set ops), T1/T2 aliases removed

**Category:** 

### 32. `dog_kennels` (question #967)

**Question:** Count the number of dogs that went through a treatment.

**Gold:**
```sql
SELECT count(DISTINCT dog_id) FROM Treatments
```

**dev_zero_shot:**
```sql
SELECT COUNT(dog_id) FROM Treatments
```

**dev_qlora_r16_final:**
```sql
SELECT count(DISTINCT dog_id) FROM treatments
```

**Auto tags:** DISTINCT added

**Category:** 

### 33. `course_teach` (question #401)

**Question:** Show names of teachers and the courses they are arranged to teach in ascending alphabetical order of the teacher's name.

**Gold:**
```sql
SELECT T3.Name ,  T2.Course FROM course_arrange AS T1 JOIN course AS T2 ON T1.Course_ID  =  T2.Course_ID JOIN teacher AS T3 ON T1.Teacher_ID  =  T3.Teacher_ID ORDER BY T3.Name
```

**dev_zero_shot:**
```sql
SELECT T2.Name, T1.Course FROM course AS T1 INNER JOIN teacher AS T2 ON T1.Course_ID = T2.Course_ID ORDER BY T2.Name ASC
```

*Did not run:* `OperationalError: no such column: T2.Course_ID`

**dev_qlora_r16_final:**
```sql
SELECT T1.Name ,  T3.Course FROM teacher AS T1 JOIN course_arrange AS T2 ON T1.Teacher_ID  =  T2.Teacher_ID JOIN course AS T3 ON T2.Course_ID  =  T3.Course_ID ORDER BY T1.Name ASC
```

**Auto tags:** now runs, joins 1->2

**Category:** 

### 34. `car_1` (question #133)

**Question:** Which model saves the most gasoline? That is to say, have the maximum miles per gallon.

**Gold:**
```sql
SELECT T1.Model FROM CAR_NAMES AS T1 JOIN CARS_DATA AS T2 ON T1.MakeId  =  T2.Id ORDER BY T2.mpg DESC LIMIT 1;
```

**dev_zero_shot:**
```sql
SELECT T1.Model FROM model_list AS T1 INNER JOIN cars_data AS T2 ON T1.ModelId = T2.Id ORDER BY T2.MPG DESC LIMIT 1
```

**dev_qlora_r16_final:**
```sql
SELECT T1.Model FROM model_list AS T1 JOIN car_names AS T2 ON T1.Model  =  T2.Model JOIN cars_data AS T3 ON T2.MakeId  =  T3.Id ORDER BY T3.MPG DESC LIMIT 1
```

**Auto tags:** joins 1->2

**Category:** 

### 35. `world_1` (question #723)

**Question:** How many people live in Asia, and what is the largest GNP among them?

**Gold:**
```sql
SELECT sum(Population) ,  max(GNP) FROM country WHERE Continent  =  "Asia"
```

**dev_zero_shot:**
```sql
SELECT SUM(T1.Population), MAX(T1.GNP) FROM country AS T1 INNER JOIN city AS T2 ON T1.Code = T2.CountryCode WHERE T1.Continent = 'Asia'
```

**dev_qlora_r16_final:**
```sql
SELECT SUM(Population) ,  MAX(GNP) FROM country WHERE Continent  =  'Asia'
```

**Auto tags:** joins 1->0, T1/T2 aliases removed

**Category:** 

### 36. `network_1` (question #906)

**Question:** What is the name of the high schooler who has the greatest number of likes?

**Gold:**
```sql
SELECT T2.name FROM Likes AS T1 JOIN Highschooler AS T2 ON T1.student_id  =  T2.id GROUP BY T1.student_id ORDER BY count(*) DESC LIMIT 1
```

**dev_zero_shot:**
```sql
SELECT T1.name FROM Highschooler AS T1 JOIN Likes AS T2 ON T1.ID  =  T2.student_id GROUP BY T1.name ORDER BY count(*) DESC LIMIT 1
```

**dev_qlora_r16_final:**
```sql
SELECT T1.name FROM Highschooler AS T1 JOIN Likes AS T2 ON T1.id  =  T2.student_id GROUP BY T2.student_id ORDER BY count(*) DESC LIMIT 1
```

**Auto tags:** none

**Category:** 

### 37. `flight_2` (question #232)

**Question:** What is the abbreviation of the airilne has the fewest flights and what country is it in?

**Gold:**
```sql
SELECT T1.Abbreviation ,  T1.Country FROM AIRLINES AS T1 JOIN FLIGHTS AS T2 ON T1.uid  =  T2.Airline GROUP BY T1.Airline ORDER BY count(*) LIMIT 1
```

**dev_zero_shot:**
```sql
SELECT T1.Abbreviation, T1.Country FROM airlines AS T1 JOIN flights AS T2 ON T1.uid = T2.Airline GROUP BY T1.uid ORDER BY COUNT(*) ASC LIMIT 1
```

**dev_qlora_r16_final:**
```sql
SELECT T1.Abbreviation ,  T1.Country FROM airlines AS T1 JOIN flights AS T2 ON T1.uid  =  T2.Airline GROUP BY T1.Airline ORDER BY count(*) LIMIT 1
```

**Auto tags:** none

**Category:** 

### 38. `tvshow` (question #635)

**Question:** which countries' tv channels are not playing any cartoon written by Todd Casey?

**Gold:**
```sql
SELECT country FROM TV_Channel EXCEPT SELECT T1.country FROM TV_Channel AS T1 JOIN cartoon AS T2 ON T1.id = T2.Channel WHERE T2.written_by  =  'Todd Casey'
```

**dev_zero_shot:**
```sql
SELECT Country FROM TV_Channel WHERE id NOT IN ( SELECT Channel FROM Cartoon WHERE Written_by = 'Todd Casey' )
```

**dev_qlora_r16_final:**
```sql
SELECT country FROM TV_channel EXCEPT SELECT t2.country FROM cartoon AS t1 JOIN TV_channel AS t2 ON t1.channel  =  t2.id WHERE t1.written_by  =  "Todd Casey"
```

**Auto tags:** joins 0->1, T1/T2 aliases added

**Category:** 

### 39. `dog_kennels` (question #980)

**Question:** How many owners temporarily do not have any dogs?

**Gold:**
```sql
SELECT count(*) FROM Owners WHERE owner_id NOT IN ( SELECT owner_id FROM Dogs )
```

**dev_zero_shot:**
```sql
SELECT count(*) FROM Owners WHERE owner_id NOT IN ( SELECT owner_id FROM Dogs WHERE abandoned_yn = 'N' )
```

**dev_qlora_r16_final:**
```sql
SELECT count(*) FROM owners WHERE owner_id NOT IN (SELECT owner_id FROM dogs)
```

**Auto tags:** none

**Category:** 

### 40. `world_1` (question #714)

**Question:** What are the population and life expectancies in Brazil?

**Gold:**
```sql
SELECT Population ,  LifeExpectancy FROM country WHERE Name  =  "Brazil"
```

**dev_zero_shot:**
```sql
SELECT T1.Population, T1.LifeExpectancy FROM country AS T1 JOIN city AS T2 ON T1.Code = T2.CountryCode WHERE T2.Name = 'Brazil'
```

**dev_qlora_r16_final:**
```sql
SELECT Population ,  LifeExpectancy FROM country WHERE Name  =  'Brazil'
```

**Auto tags:** joins 1->0, T1/T2 aliases removed

**Category:** 

### 41. `car_1` (question #178)

**Question:** What are the ids and names of all countries that either have more than 3 car makers or produce fiat model ?

**Gold:**
```sql
select t1.countryid ,  t1.countryname from countries as t1 join car_makers as t2 on t1.countryid  =  t2.country group by t1.countryid having count(*)  >  3 union select t1.countryid ,  t1.countryname from countries as t1 join car_makers as t2 on t1.countryid  =  t2.country join model_list as t3 on t2.id  =  t3.maker where t3.model  =  'fiat';
```

**dev_zero_shot:**
```sql
SELECT T1.CountryId, T1.CountryName FROM countries AS T1 JOIN car_makers AS T2 ON T1.CountryId = T2.Country WHERE T2.CountryId > 3 OR T1.CountryName = 'Fiat'
```

*Did not run:* `OperationalError: no such column: T2.CountryId`

**dev_qlora_r16_final:**
```sql
SELECT T1.Countryid ,  T1.CountryName FROM countries AS T1 JOIN car_makers AS T2 ON T1.Countryid  =  T2.Country GROUP BY T1.Countryid HAVING count(*)  >  3 UNION SELECT T1.Countryid ,  T1.CountryName FROM countries AS T1 JOIN car_makers AS T2 ON T1.Countryid  =  T2.Country JOIN model_list AS T3 ON T2.id  =  T3.Maker WHERE T3.Model  =  "fiat"
```

**Auto tags:** now runs, joins 1->3, SELECTs 1->2 (subqueries/set ops), GROUP BY added, HAVING added

**Category:** 

### 42. `world_1` (question #796)

**Question:** Find the government form name and total population for each government form whose average life expectancy is longer than 72.

**Gold:**
```sql
SELECT sum(Population) ,  GovernmentForm FROM country GROUP BY GovernmentForm HAVING avg(LifeExpectancy)  >  72
```

**dev_zero_shot:**
```sql
SELECT T1.GovernmentForm, SUM(T1.Population) FROM country AS T1 JOIN countrylanguage AS T2 ON T1.Code = T2.CountryCode GROUP BY T1.GovernmentForm HAVING AVG(T1.LifeExpectancy) > 72
```

**dev_qlora_r16_final:**
```sql
SELECT GovernmentForm ,  SUM(Population) FROM country GROUP BY GovernmentForm HAVING AVG(LifeExpectancy)  >  72
```

**Auto tags:** joins 1->0, T1/T2 aliases removed

**Category:** 

### 43. `cre_Doc_Template_Mgt` (question #380)

**Question:** What are the ids of documents that contain the paragraph text 'Brazil' and 'Ireland'?

**Gold:**
```sql
SELECT document_id FROM Paragraphs WHERE paragraph_text  =  'Brazil' INTERSECT SELECT document_id FROM Paragraphs WHERE paragraph_text  =  'Ireland'
```

**dev_zero_shot:**
```sql
SELECT Document_ID FROM Paragraphs WHERE Paragraph_Text LIKE '%Brazil%' AND Paragraph_Text LIKE '%Ireland%'
```

**dev_qlora_r16_final:**
```sql
SELECT document_id FROM paragraphs WHERE paragraph_text  =  'Brazil' INTERSECT SELECT document_id FROM paragraphs WHERE paragraph_text  =  'Ireland'
```

**Auto tags:** SELECTs 1->2 (subqueries/set ops)

**Category:** 

### 44. `flight_2` (question #231)

**Question:** Find the abbreviation and country of the airline that has fewest number of flights?

**Gold:**
```sql
SELECT T1.Abbreviation ,  T1.Country FROM AIRLINES AS T1 JOIN FLIGHTS AS T2 ON T1.uid  =  T2.Airline GROUP BY T1.Airline ORDER BY count(*) LIMIT 1
```

**dev_zero_shot:**
```sql
SELECT T1.Abbreviation, T1.Country FROM airlines AS T1 JOIN flights AS T2 ON T1.uid = T2.Airline GROUP BY T1.uid ORDER BY COUNT(*) ASC LIMIT 1
```

**dev_qlora_r16_final:**
```sql
SELECT T1.Abbreviation ,  T1.Country FROM airlines AS T1 JOIN flights AS T2 ON T1.uid  =  T2.Airline GROUP BY T1.Airline ORDER BY count(*) LIMIT 1
```

**Auto tags:** none

**Category:** 

### 45. `dog_kennels` (question #922)

**Question:** Which professionals live in the state of Indiana or have done treatment on more than 2 treatments? List his or her id, last name and cell phone.

**Gold:**
```sql
SELECT professional_id ,  last_name ,  cell_number FROM Professionals WHERE state  =  'Indiana' UNION SELECT T1.professional_id ,  T1.last_name ,  T1.cell_number FROM Professionals AS T1 JOIN Treatments AS T2 ON T1.professional_id  =  T2.professional_id GROUP BY T1.professional_id HAVING count(*)  >  2
```

**dev_zero_shot:**
```sql
SELECT DISTINCT T1.professional_id, T1.last_name, T1.cell_number FROM Professionals AS T1 JOIN Treatments AS T2 ON T1.professional_id = T2.professional_id WHERE T1.state = 'Indiana' OR T2.professional_id IN ( SELECT professional_id FROM Treatments GROUP BY professional_id HAVING COUNT(*) > 2 )
```

**dev_qlora_r16_final:**
```sql
SELECT T1.professional_id ,  T1.last_name ,  T1.cell_number FROM Professionals AS T1 JOIN Treatments AS T2 ON T1.professional_id  =  T2.professional_id GROUP BY T1.professional_id HAVING count(*)  >  2 UNION SELECT professional_id ,  last_name ,  cell_number FROM Professionals WHERE state  =  "Indiana"
```

**Auto tags:** DISTINCT removed

**Category:** 

### 46. `cre_Doc_Template_Mgt` (question #341)

**Question:** Show all template type codes and the number of documents using each type.

**Gold:**
```sql
SELECT T1.template_type_code ,  count(*) FROM Templates AS T1 JOIN Documents AS T2 ON T1.template_id  =  T2.template_id GROUP BY T1.template_type_code
```

**dev_zero_shot:**
```sql
SELECT T1.Template_Type_Code, COUNT(T2.Document_ID) AS Number_of_Documents
FROM Ref_Template_Types AS T1
JOIN Templates AS T2 ON T1.Template_Type_Code = T2.Template_Type_Code
JOIN Documents AS T3 ON T2.Template_ID = T3.Template_ID
GROUP BY T1.Template_Type_Code
```

*Did not run:* `OperationalError: no such column: T2.Document_ID`

**dev_qlora_r16_final:**
```sql
SELECT T1.template_type_code ,  count(*) FROM Templates AS T1 JOIN Documents AS T2 ON T1.template_id  =  T2.template_id GROUP BY T1.template_type_code
```

**Auto tags:** now runs, joins 2->1

**Category:** 

### 47. `tvshow` (question #638)

**Question:** What is the series name and country of all TV channels that are playing cartoons directed by Ben Jones and cartoons directed by Michael Chang?

**Gold:**
```sql
SELECT T1.series_name ,  T1.country FROM TV_Channel AS T1 JOIN cartoon AS T2 ON T1.id = T2.Channel WHERE T2.directed_by  =  'Michael Chang' INTERSECT SELECT T1.series_name ,  T1.country FROM TV_Channel AS T1 JOIN cartoon AS T2 ON T1.id = T2.Channel WHERE T2.directed_by  =  'Ben Jones'
```

**dev_zero_shot:**
```sql
SELECT T1.series_name, T1.Country FROM TV_Channel AS T1 JOIN Cartoon AS T2 ON T1.id = T2.Channel WHERE T2.Directed_by = 'Ben Jones' OR T2.Directed_by = 'Michael Chang'
```

**dev_qlora_r16_final:**
```sql
SELECT T2.series_name ,  T2.Country FROM Cartoon AS T1 JOIN TV_Channel AS T2 ON T1.Channel  =  T2.id WHERE T1.directed_by  =  "Ben Jones" INTERSECT SELECT T2.series_name ,  T2.Country FROM Cartoon AS T1 JOIN TV_Channel AS T2 ON T1.Channel  =  T2.id WHERE T1.directed_by  =  "Michael Chang"
```

**Auto tags:** joins 1->2, SELECTs 1->2 (subqueries/set ops)

**Category:** 

### 48. `course_teach` (question #402)

**Question:** What are the names of the teachers and the courses they teach in ascending alphabetical order by the name of the teacher?

**Gold:**
```sql
SELECT T3.Name ,  T2.Course FROM course_arrange AS T1 JOIN course AS T2 ON T1.Course_ID  =  T2.Course_ID JOIN teacher AS T3 ON T1.Teacher_ID  =  T3.Teacher_ID ORDER BY T3.Name
```

**dev_zero_shot:**
```sql
SELECT T2.Name, T1.Course FROM course AS T1 INNER JOIN teacher AS T2 ON T1.Course_ID = T2.Course_ID ORDER BY T2.Name ASC
```

*Did not run:* `OperationalError: no such column: T2.Course_ID`

**dev_qlora_r16_final:**
```sql
SELECT T1.Name ,  T3.Course FROM teacher AS T1 JOIN course_arrange AS T2 ON T1.Teacher_ID  =  T2.Teacher_ID JOIN course AS T3 ON T2.Course_ID  =  T3.Course_ID ORDER BY T1.Name ASC
```

**Auto tags:** now runs, joins 1->2

**Category:** 

### 49. `battle_death` (question #505)

**Question:** Show names, results and bulgarian commanders of the battles with no ships lost in the 'English Channel'.

**Gold:**
```sql
SELECT name ,  RESULT ,  bulgarian_commander FROM battle EXCEPT SELECT T1.name ,  T1.result ,  T1.bulgarian_commander FROM battle AS T1 JOIN ship AS T2 ON T1.id  =  T2.lost_in_battle WHERE T2.location  =  'English Channel'
```

**dev_zero_shot:**
```sql
SELECT T1.name, T1.result, T1.bulgarian_commander FROM battle AS T1 JOIN ship AS T2 ON T1.id = T2.lost_in_battle WHERE T2.location != 'English Channel'
```

**dev_qlora_r16_final:**
```sql
SELECT name ,  result ,  bulgarian_commander FROM battle WHERE id NOT IN (SELECT lost_in_battle FROM ship WHERE location  =  'English Channel')
```

**Auto tags:** joins 1->0, SELECTs 1->2 (subqueries/set ops), T1/T2 aliases removed

**Category:** 

### 50. `course_teach` (question #399)

**Question:** Show names of teachers and the courses they are arranged to teach.

**Gold:**
```sql
SELECT T3.Name ,  T2.Course FROM course_arrange AS T1 JOIN course AS T2 ON T1.Course_ID  =  T2.Course_ID JOIN teacher AS T3 ON T1.Teacher_ID  =  T3.Teacher_ID
```

**dev_zero_shot:**
```sql
SELECT T2.Name, T1.Course FROM course AS T1 JOIN teacher AS T2 ON T1.Course_ID = T2.Course_ID
```

*Did not run:* `OperationalError: no such column: T2.Course_ID`

**dev_qlora_r16_final:**
```sql
SELECT T1.Name ,  T3.Course FROM teacher AS T1 JOIN course_arrange AS T2 ON T1.Teacher_ID  =  T2.Teacher_ID JOIN course AS T3 ON T2.Course_ID  =  T3.Course_ID
```

**Auto tags:** now runs, joins 1->2

**Category:** 

### 51. `network_1` (question #907)

**Question:** Give the name of the student with the most likes.

**Gold:**
```sql
SELECT T2.name FROM Likes AS T1 JOIN Highschooler AS T2 ON T1.student_id  =  T2.id GROUP BY T1.student_id ORDER BY count(*) DESC LIMIT 1
```

**dev_zero_shot:**
```sql
SELECT T1.name FROM Highschooler AS T1 JOIN Likes AS T2 ON T1.ID  =  T2.student_id GROUP BY T1.name ORDER BY count(*) DESC LIMIT 1
```

**dev_qlora_r16_final:**
```sql
SELECT T1.name FROM Highschooler AS T1 JOIN Likes AS T2 ON T1.id  =  T2.student_id GROUP BY T2.student_id ORDER BY count(*) DESC LIMIT 1
```

**Auto tags:** none

**Category:** 

### 52. `wta_1` (question #451)

**Question:** What are the country code and first name of the players who won in both tourney WTA Championships and Australian Open?

**Gold:**
```sql
SELECT T1.country_code ,  T1.first_name FROM players AS T1 JOIN matches AS T2 ON T1.player_id  =  T2.winner_id WHERE T2.tourney_name  =  'WTA Championships' INTERSECT SELECT T1.country_code ,  T1.first_name FROM players AS T1 JOIN matches AS T2 ON T1.player_id  =  T2.winner_id WHERE T2.tourney_name  =  'Australian Open'
```

**dev_zero_shot:**
```sql
SELECT DISTINCT T1.country_code, T1.first_name FROM players AS T1 JOIN matches AS T2 ON T1.player_id = T2.winner_id WHERE T2.tourney_name IN ('WTA Championships', 'Australian Open')
```

**dev_qlora_r16_final:**
```sql
SELECT T1.country_code ,  T1.first_name FROM players AS T1 JOIN matches AS T2 ON T1.player_id  =  T2.winner_id WHERE T2.tourney_name  =  'WTA Championships' INTERSECT SELECT T1.country_code ,  T1.first_name FROM players AS T1 JOIN matches AS T2 ON T1.player_id  =  T2.winner_id WHERE T2.tourney_name  =  'Australian Open'
```

**Auto tags:** joins 1->2, SELECTs 1->2 (subqueries/set ops), DISTINCT removed

**Category:** 

### 53. `student_transcripts_tracking` (question #531)

**Question:** What is the description of the department whose name has the substring the computer?

**Gold:**
```sql
SELECT department_description FROM Departments WHERE department_name LIKE '%computer%'
```

**dev_zero_shot:**
```sql
SELECT department_description FROM Departments WHERE department_name LIKE '%the computer%'
```

**dev_qlora_r16_final:**
```sql
SELECT department_description FROM DEPARTMENTS WHERE department_name LIKE "%computer%"
```

**Auto tags:** none

**Category:** 

### 54. `student_transcripts_tracking` (question #533)

**Question:** Who are enrolled in 2 degree programs in one semester? List the first name, middle name and last name and the id.

**Gold:**
```sql
SELECT T1.first_name ,  T1.middle_name ,  T1.last_name ,  T1.student_id FROM Students AS T1 JOIN Student_Enrolment AS T2 ON T1.student_id  =  T2.student_id GROUP BY T1.student_id HAVING count(*)  =  2
```

**dev_zero_shot:**
```sql
SELECT T1.first_name, T1.middle_name, T1.last_name, T1.student_id FROM Students AS T1 JOIN Student_Enrolment AS T2 ON T1.student_id = T2.student_id GROUP BY T1.student_id HAVING COUNT(DISTINCT T2.degree_program_id) = 2
```

**dev_qlora_r16_final:**
```sql
SELECT T1.first_name ,  T1.middle_name ,  T1.last_name ,  T1.student_id FROM Students AS T1 JOIN Student_Enrolment AS T2 ON T1.student_id  =  T2.student_id GROUP BY T1.student_id HAVING count(*)  =  2
```

**Auto tags:** DISTINCT removed

**Category:** 

### 55. `cre_Doc_Template_Mgt` (question #353)

**Question:** What are the distinct template type descriptions for the templates ever used by any document?

**Gold:**
```sql
SELECT DISTINCT T1.template_type_description FROM Ref_template_types AS T1 JOIN Templates AS T2 ON T1.template_type_code  = T2.template_type_code JOIN Documents AS T3 ON T2.Template_ID  =  T3.template_ID
```

**dev_zero_shot:**
```sql
SELECT DISTINCT T2.Template_Type_Description FROM Documents AS T1 INNER JOIN Templates AS T2 ON T1.Template_ID = T2.Template_ID
```

*Did not run:* `OperationalError: no such column: T2.Template_Type_Description`

**dev_qlora_r16_final:**
```sql
SELECT DISTINCT T1.template_type_description FROM Ref_template_types AS T1 JOIN templates AS T2 ON T1.template_type_code  =  T2.template_type_code JOIN documents AS T3 ON T2.template_id  =  T3.template_id
```

**Auto tags:** now runs, joins 1->2

**Category:** 

### 56. `car_1` (question #94)

**Question:** What is the full name of each car maker, along with its id and how many models it produces?

**Gold:**
```sql
SELECT T1.FullName ,  T1.Id ,  count(*) FROM CAR_MAKERS AS T1 JOIN MODEL_LIST AS T2 ON T1.Id  =  T2.Maker GROUP BY T1.Id;
```

**dev_zero_shot:**
```sql
SELECT T1.Maker, T1.Id, COUNT(T2.Model) FROM car_makers AS T1 INNER JOIN model_list AS T2 ON T1.Id = T2.Maker GROUP BY T1.Id
```

**dev_qlora_r16_final:**
```sql
SELECT T1.FullName ,  T1.id ,  count(*) FROM car_makers AS T1 JOIN model_list AS T2 ON T1.id  =  T2.Maker GROUP BY T1.id
```

**Auto tags:** none

**Category:** 

### 57. `wta_1` (question #452)

**Question:** What are the first names and country codes for players who won both the WTA Championships and the Australian Open?

**Gold:**
```sql
SELECT T1.country_code ,  T1.first_name FROM players AS T1 JOIN matches AS T2 ON T1.player_id  =  T2.winner_id WHERE T2.tourney_name  =  'WTA Championships' INTERSECT SELECT T1.country_code ,  T1.first_name FROM players AS T1 JOIN matches AS T2 ON T1.player_id  =  T2.winner_id WHERE T2.tourney_name  =  'Australian Open'
```

**dev_zero_shot:**
```sql
SELECT DISTINCT p.first_name, p.country_code FROM players p JOIN matches m ON p.player_id = m.winner_id WHERE m.tourney_name IN ('WTA Championships', 'Australian Open')
```

**dev_qlora_r16_final:**
```sql
SELECT T1.first_name ,  T1.country_code FROM players AS T1 JOIN matches AS T2 ON T1.player_id  =  T2.winner_id WHERE T2.tourney_name  =  'WTA Championships' INTERSECT SELECT T1.first_name ,  T1.country_code FROM players AS T1 JOIN matches AS T2 ON T1.player_id  =  T2.winner_id WHERE T2.tourney_name  =  'Australian Open'
```

**Auto tags:** joins 1->2, SELECTs 1->2 (subqueries/set ops), DISTINCT removed, T1/T2 aliases added

**Category:** 

### 58. `dog_kennels` (question #956)

**Question:** Which dogs are owned by someone who lives in Virginia? List the owner's first name and the dog's name.

**Gold:**
```sql
SELECT T1.first_name ,  T2.name FROM Owners AS T1 JOIN Dogs AS T2 ON T1.owner_id  =  T2.owner_id WHERE T1.state  =  'Virginia'
```

**dev_zero_shot:**
```sql
SELECT O.first_name, D.name FROM Owners O JOIN Dogs D ON O.owner_id = D.owner_id WHERE O.state = 'VA'
```

**dev_qlora_r16_final:**
```sql
SELECT T1.first_name ,  T3.name FROM Owners AS T1 JOIN Dogs AS T3 ON T1.owner_id  =  T3.owner_id WHERE T1.state  =  "Virginia"
```

**Auto tags:** T1/T2 aliases added

**Category:** 

### 59. `network_1` (question #898)

**Question:** Show the ids of high schoolers who have friends and are also liked by someone else.

**Gold:**
```sql
SELECT student_id FROM Friend INTERSECT SELECT liked_id FROM Likes
```

**dev_zero_shot:**
```sql
SELECT student_id FROM Friend INTERSECT SELECT student_id FROM Likes
```

**dev_qlora_r16_final:**
```sql
SELECT student_id FROM friend INTERSECT SELECT liked_id FROM likes
```

**Auto tags:** none

**Category:** 

### 60. `course_teach` (question #404)

**Question:** What are the names of the people who teach math courses?

**Gold:**
```sql
SELECT T3.Name FROM course_arrange AS T1 JOIN course AS T2 ON T1.Course_ID  =  T2.Course_ID JOIN teacher AS T3 ON T1.Teacher_ID  =  T3.Teacher_ID WHERE T2.Course  =  "Math"
```

**dev_zero_shot:**
```sql
SELECT T2.Name FROM course AS T1 JOIN teacher AS T2 ON T1.Course_ID = T2.Course_ID WHERE T1.Course = 'Math'
```

*Did not run:* `OperationalError: no such column: T2.Course_ID`

**dev_qlora_r16_final:**
```sql
SELECT T2.Name FROM course_arrange AS T1 JOIN teacher AS T2 ON T1.Teacher_ID  =  T2.Teacher_ID JOIN course AS T3 ON T1.Course_ID  =  T3.Course_ID WHERE T3.Course  =  "Math"
```

**Auto tags:** now runs, joins 1->2

**Category:** 

### 61. `dog_kennels` (question #927)

**Question:** Find the first names that are used for professionals or owners but are not used as dog names.

**Gold:**
```sql
SELECT first_name FROM Professionals UNION SELECT first_name FROM Owners EXCEPT SELECT name FROM Dogs
```

**dev_zero_shot:**
```sql
SELECT first_name FROM Owners EXCEPT SELECT first_name FROM Dogs UNION SELECT first_name FROM Professionals
```

*Did not run:* `OperationalError: no such column: first_name`

**dev_qlora_r16_final:**
```sql
SELECT first_name FROM owners EXCEPT SELECT name FROM dogs UNION SELECT first_name FROM professionals
```

**Auto tags:** now runs

**Category:** 


## Broken: right in dev_zero_shot, wrong in dev_qlora_r16_final

### 1. `pets_1` (question #68)

**Question:** What type of pet is the youngest animal, and how much does it weigh?

**Gold:**
```sql
SELECT pettype ,  weight FROM pets ORDER BY pet_age LIMIT 1
```

**dev_zero_shot:**
```sql
SELECT PetType, weight FROM Pets ORDER BY pet_age ASC LIMIT 1
```

**dev_qlora_r16_final:**
```sql
SELECT pet_type ,  weight FROM pets ORDER BY pet_age LIMIT 1
```

*Did not run:* `OperationalError: no such column: pet_type`

**Auto tags:** no longer runs

**Category:** 
 inccorect column name
### 2. `voter_1` (question #698)

**Question:** What is the area code in which the most voters voted?

**Gold:**
```sql
SELECT T1.area_code FROM area_code_state AS T1 JOIN votes AS T2 ON T1.state  =  T2.state GROUP BY T1.area_code ORDER BY count(*) DESC LIMIT 1
```

**dev_zero_shot:**
```sql
SELECT T1.area_code FROM AREA_CODE_STATE AS T1 JOIN VOTES AS T2 ON T1.state = T2.state GROUP BY T1.area_code ORDER BY COUNT(*) DESC LIMIT 1
```

**dev_qlora_r16_final:**
```sql
SELECT area_code FROM area_code_state WHERE state IN (SELECT state FROM votes GROUP BY state ORDER BY count(*) DESC LIMIT 1)
```

**Auto tags:** joins 1->0, SELECTs 1->2 (subqueries/set ops), T1/T2 aliases removed

**Category:** 
missing join
### 3. `real_estate_properties` (question #1031)

**Question:** What is the feature type name of feature AirCon?

**Gold:**
```sql
SELECT T2.feature_type_name FROM Other_Available_Features AS T1 JOIN Ref_Feature_Types AS T2 ON T1.feature_type_code  =  T2.feature_type_code WHERE T1.feature_name  =  "AirCon"
```

**dev_zero_shot:**
```sql
SELECT feature_type_name FROM Ref_Feature_Types WHERE feature_type_code = (SELECT feature_type_code FROM Other_Available_Features WHERE feature_name = 'AirCon')
```

**dev_qlora_r16_final:**
```sql
SELECT feature_type_name FROM Ref_Feature_Types WHERE feature_type_code  =  "AirCon"
```

**Auto tags:** SELECTs 2->1 (subqueries/set ops)

**Category:** 
missing join/sub query
### 4. `car_1` (question #162)

**Question:** What is the number of countries with more than 2 car makers ?

**Gold:**
```sql
select count(*) from countries as t1 join car_makers as t2 on t1.countryid  =  t2.country group by t1.countryid having count(*)  >  2
```

**dev_zero_shot:**
```sql
SELECT COUNT(Country) FROM car_makers GROUP BY Country HAVING COUNT(Maker) > 2
```

**dev_qlora_r16_final:**
```sql
SELECT count(*) FROM (SELECT T1.Country FROM countries AS T1 JOIN car_makers AS T2 ON T1.CountryId  =  T2.Country GROUP BY T1.Country HAVING count(*)  >  2)
```

*Did not run:* `OperationalError: no such column: T1.Country`

**Auto tags:** no longer runs, joins 0->1, SELECTs 1->2 (subqueries/set ops), T1/T2 aliases added

**Category:** 
reference wrong column from table
### 5. `car_1` (question #100)

**Question:** What is the name of the different car makers who produced a car in 1970?

**Gold:**
```sql
SELECT DISTINCT T1.Maker FROM CAR_MAKERS AS T1 JOIN MODEL_LIST AS T2 ON T1.Id  =  T2.Maker JOIN CAR_NAMES AS T3 ON T2.model  =  T3.model JOIN CARS_DATA AS T4 ON T3.MakeId  =  T4.id WHERE T4.year  =  '1970';
```

**dev_zero_shot:**
```sql
SELECT DISTINCT T1.Maker FROM car_makers AS T1 INNER JOIN model_list AS T2 ON T1.Id = T2.Maker INNER JOIN car_names AS T3 ON T2.Model = T3.Model INNER JOIN cars_data AS T4 ON T3.MakeId = T4.Id WHERE T4.Year = 1970
```

**dev_qlora_r16_final:**
```sql
SELECT DISTINCT T1.Maker FROM car_makers AS T1 JOIN car_names AS T2 ON T1.Id  =  T2.MakeId JOIN cars_data AS T3 ON T2.MakeId  =  T3.Id WHERE T3.Year  =  1970
```

**Auto tags:** joins 3->2

**Category:** 
missing join
### 6. `cre_Doc_Template_Mgt` (question #374)

**Question:** Return the id and name of the document with the most paragraphs.

**Gold:**
```sql
SELECT T1.document_id ,  T2.document_name FROM Paragraphs AS T1 JOIN Documents AS T2 ON T1.document_id  =  T2.document_id GROUP BY T1.document_id ORDER BY count(*) DESC LIMIT 1
```

**dev_zero_shot:**
```sql
SELECT T1.Document_ID, T1.Document_Name FROM Documents AS T1 JOIN Paragraphs AS T2 ON T1.Document_ID = T2.Document_ID GROUP BY T1.Document_ID, T1.Document_Name ORDER BY COUNT(T2.Paragraph_ID) DESC LIMIT 1
```

**dev_qlora_r16_final:**
```sql
SELECT T1.document_id ,  T2.document_name FROM Documents AS T1 JOIN Documents AS T2 ON T1.document_id  =  T2.document_id GROUP BY T1.document_id ORDER BY count(*) DESC LIMIT 1
```

**Auto tags:** none

**Category:** 
incorrect join
### 7. `dog_kennels` (question #933)

**Question:** What are the id, role, and first name of the professionals who have performed two or more treatments?

**Gold:**
```sql
SELECT T1.professional_id ,  T1.role_code ,  T1.first_name FROM Professionals AS T1 JOIN Treatments AS T2 ON T1.professional_id  =  T2.professional_id GROUP BY T1.professional_id HAVING count(*)  >=  2
```

**dev_zero_shot:**
```sql
SELECT T1.professional_id, T1.role_code, T1.first_name FROM Professionals AS T1 JOIN Treatments AS T2 ON T1.professional_id = T2.professional_id GROUP BY T1.professional_id HAVING COUNT(T2.treatment_id) >= 2
```

**dev_qlora_r16_final:**
```sql
SELECT T1.professional_id ,  T1.first_name ,  T1.last_name FROM Professionals AS T1 JOIN Treatments AS T2 ON T1.professional_id  =  T2.professional_id GROUP BY T1.professional_id HAVING count(*)  >=  2
```

**Auto tags:** none

**Category:** 
see no issue?
### 8. `pets_1` (question #65)

**Question:** Find the first name and age of students who have a dog but do not have a cat as a pet.

**Gold:**
```sql
SELECT T1.fname ,  T1.age FROM student AS T1 JOIN has_pet AS T2 ON T1.stuid  =  T2.stuid JOIN pets AS T3 ON T3.petid  =  T2.petid WHERE T3.pettype  =  'dog' AND T1.stuid NOT IN (SELECT T1.stuid FROM student AS T1 JOIN has_pet AS T2 ON T1.stuid  =  T2.stuid JOIN pets AS T3 ON T3.petid  =  T2.petid WHERE T3.pettype  =  'cat')
```

**dev_zero_shot:**
```sql
SELECT T1.Fname, T1.Age FROM Student AS T1 JOIN Has_Pet AS T2 ON T1.StuID = T2.StuID JOIN Pets AS T3 ON T2.PetID = T3.PetID WHERE T3.PetType = 'dog' AND T1.StuID NOT IN (SELECT StuID FROM Has_Pet JOIN Pets ON Has_Pet.PetID = Pets.PetID WHERE Pets.PetType = 'cat')
```

**dev_qlora_r16_final:**
```sql
SELECT fname ,  age FROM Student WHERE StuID IN (SELECT StuID FROM Has_Pet AS T1 JOIN Pets AS T2 ON T1.PetID  =  T2.PetID WHERE T2.PetType  =  "dog" EXCEPT SELECT StuID FROM Has_Pet AS T1 JOIN Pets AS T2 ON T1.PetID  =  T2.PetID WHERE T2.PetType  =  "cat")
```

**Auto tags:** joins 3->2, SELECTs 2->3 (subqueries/set ops)

**Category:** 
missing join?
### 9. `tvshow` (question #646)

**Question:** What are the package options of all tv channels that are not playing any cartoons directed by Ben Jones?

**Gold:**
```sql
SELECT package_option FROM TV_Channel WHERE id NOT IN (SELECT channel FROM cartoon WHERE directed_by  =  'Ben Jones')
```

**dev_zero_shot:**
```sql
SELECT Package_Option FROM TV_Channel WHERE id NOT IN ( SELECT Channel FROM Cartoon WHERE Directed_by = 'Ben Jones' )
```

**dev_qlora_r16_final:**
```sql
SELECT Package_Option FROM TV_Channel EXCEPT SELECT T2.Package_Option FROM Cartoon AS T1 JOIN TV_Channel AS T2 ON T1.Channel  =  T2.id WHERE T1.directed_by  =  "Ben Jones"
```

**Auto tags:** joins 0->1, T1/T2 aliases added

**Category:** 
unecessary join
### 10. `pets_1` (question #71)

**Question:** Find the average and maximum age for each type of pet.

**Gold:**
```sql
SELECT avg(pet_age) ,  max(pet_age) ,  pettype FROM pets GROUP BY pettype
```

**dev_zero_shot:**
```sql
SELECT PetType, AVG(pet_age) AS avg_age, MAX(pet_age) AS max_age FROM Pets GROUP BY PetType
```

**dev_qlora_r16_final:**
```sql
SELECT pet_type ,  avg(pet_age) ,  max(pet_age) FROM pets GROUP BY pet_type
```

*Did not run:* `OperationalError: no such column: pet_type`

**Auto tags:** no longer runs

**Category:** 
incorrect column name
### 11. `dog_kennels` (question #936)

**Question:** Which owner has paid for the most treatments on his or her dogs? List the owner id and last name.

**Gold:**
```sql
SELECT T1.owner_id ,  T1.last_name FROM Owners AS T1 JOIN Dogs AS T2 ON T1.owner_id  =  T2.owner_id JOIN Treatments AS T3 ON T2.dog_id  =  T3.dog_id GROUP BY T1.owner_id ORDER BY count(*) DESC LIMIT 1
```

**dev_zero_shot:**
```sql
SELECT T1.owner_id, T1.last_name FROM Owners AS T1 JOIN Dogs AS T2 ON T1.owner_id = T2.owner_id JOIN Treatments AS T3 ON T2.dog_id = T3.dog_id GROUP BY T1.owner_id, T1.last_name ORDER BY COUNT(T3.treatment_id) DESC LIMIT 1
```

**dev_qlora_r16_final:**
```sql
SELECT T1.owner_id ,  T2.last_name FROM Owners AS T1 JOIN Dogs AS T2 ON T1.owner_id  =  T2.owner_id JOIN Treatments AS T3 ON T2.dog_id  =  T3.dog_id GROUP BY T1.owner_id ORDER BY sum(T3.cost_of_treatment) DESC LIMIT 1
```

*Did not run:* `OperationalError: no such column: T2.last_name`

**Auto tags:** no longer runs

**Category:** 

### 12. `world_1` (question #749)

**Question:** Give the names of countries with English and French as official languages.

**Gold:**
```sql
SELECT T1.Name FROM country AS T1 JOIN countrylanguage AS T2 ON T1.Code  =  T2.CountryCode WHERE T2.Language  =  "English" AND T2.IsOfficial  =  "T" INTERSECT SELECT T1.Name FROM country AS T1 JOIN countrylanguage AS T2 ON T1.Code  =  T2.CountryCode WHERE T2.Language  =  "French" AND T2.IsOfficial  =  "T"
```

**dev_zero_shot:**
```sql
SELECT T1.Name FROM country AS T1 JOIN countrylanguage AS T2 ON T1.Code = T2.CountryCode WHERE T2.Language = 'English' AND T2.IsOfficial = 'T' AND T2.CountryCode IN ( SELECT CountryCode FROM countrylanguage WHERE Language = 'French' AND IsOfficial = 'T' )
```

**dev_qlora_r16_final:**
```sql
SELECT T1.Name FROM country AS T1 JOIN countrylanguage AS T2 ON T1.Code  =  T2.CountryCode WHERE T2.IsOfficial  =  'Yes' AND T2.Language  =  'English' INTERSECT SELECT T1.Name FROM country AS T1 JOIN countrylanguage AS T2 ON T1.Code  =  T2.CountryCode WHERE T2.IsOfficial  =  'Yes' AND T2.Language  =  'French'
```

**Auto tags:** joins 1->2

**Category:** 

### 13. `pets_1` (question #49)

**Question:** Find the maximum weight for each type of pet. List the maximum weight and pet type.

**Gold:**
```sql
SELECT max(weight) ,  petType FROM pets GROUP BY petType
```

**dev_zero_shot:**
```sql
SELECT PetType, MAX(weight) FROM Pets GROUP BY PetType
```

**dev_qlora_r16_final:**
```sql
SELECT max(weight) ,  pet_type FROM pets GROUP BY pet_type
```

*Did not run:* `OperationalError: no such column: pet_type`

**Auto tags:** no longer runs

**Category:** 

### 14. `voter_1` (question #688)

**Question:** List the contestant numbers and names, ordered by contestant name descending.

**Gold:**
```sql
SELECT contestant_number ,  contestant_name FROM contestants ORDER BY contestant_name DESC
```

**dev_zero_shot:**
```sql
SELECT T1.contestant_number, T1.contestant_name FROM CONTESTANTS AS T1 ORDER BY T1.contestant_name DESC
```

**dev_qlora_r16_final:**
```sql
SELECT T1.contestant_number ,  T1.contestant_name FROM CONTESTANTS AS T1 JOIN VOTES AS T2 ON T1.contestant_number  =  T2.contestant_number ORDER BY T1.contestant_name DESC
```

**Auto tags:** joins 0->1

**Category:** 

### 15. `dog_kennels` (question #928)

**Question:** Which professional did not operate any treatment on dogs? List the professional's id, role and email.

**Gold:**
```sql
SELECT professional_id ,  role_code ,  email_address FROM Professionals EXCEPT SELECT T1.professional_id ,  T1.role_code ,  T1.email_address FROM Professionals AS T1 JOIN Treatments AS T2 ON T1.professional_id  =  T2.professional_id
```

**dev_zero_shot:**
```sql
SELECT professional_id, role_code, email_address FROM Professionals WHERE professional_id NOT IN (SELECT professional_id FROM Treatments)
```

**dev_qlora_r16_final:**
```sql
SELECT professional_id ,  role_code ,  email_address FROM Professionals EXCEPT SELECT professional_id ,  role_code ,  email_address FROM Professionals AS T1 JOIN Treatments AS T2 ON T1.professional_id  =  T2.professional_id
```

*Did not run:* `OperationalError: ambiguous column name: professional_id`

**Auto tags:** no longer runs, joins 0->1, T1/T2 aliases added

**Category:** 

### 16. `dog_kennels` (question #921)

**Question:** Find the average age of the dogs who went through treatments.

**Gold:**
```sql
SELECT avg(age) FROM Dogs WHERE dog_id IN ( SELECT dog_id FROM Treatments )
```

**dev_zero_shot:**
```sql
SELECT AVG(age) FROM Dogs WHERE dog_id IN (SELECT dog_id FROM Treatments)
```

**dev_qlora_r16_final:**
```sql
SELECT avg(T1.age) FROM dogs AS T1 JOIN treatments AS T2 ON T1.dog_id  =  T2.dog_id
```

**Auto tags:** joins 0->1, SELECTs 2->1 (subqueries/set ops), T1/T2 aliases added

**Category:** 

### 17. `dog_kennels` (question #941)

**Question:** Find the owner id and zip code of the owner who spent the most money in total for his or her dogs.

**Gold:**
```sql
SELECT T1.owner_id ,  T1.zip_code FROM Owners AS T1 JOIN Dogs AS T2 ON T1.owner_id  =  T2.owner_id JOIN Treatments AS T3 ON T2.dog_id  =  T3.dog_id GROUP BY T1.owner_id ORDER BY sum(T3.cost_of_treatment) DESC LIMIT 1
```

**dev_zero_shot:**
```sql
SELECT T1.owner_id, T1.zip_code FROM Owners AS T1 JOIN Dogs AS T2 ON T1.owner_id = T2.owner_id JOIN Treatments AS T3 ON T2.dog_id = T3.dog_id GROUP BY T1.owner_id, T1.zip_code ORDER BY SUM(T3.cost_of_treatment) DESC LIMIT 1
```

**dev_qlora_r16_final:**
```sql
SELECT T1.owner_id ,  T1.zip_code FROM Owners AS T1 JOIN Dogs AS T2 ON T1.owner_id  =  T2.owner_id JOIN Treatments AS T3 ON T2.dog_id  =  T3.dog_id JOIN Charges AS T4 ON T3.charge_type_code  =  T4.charge_type_code GROUP BY T1.owner_id ORDER BY sum(T4.charge_amount) DESC LIMIT 1
```

*Did not run:* `OperationalError: no such column: T3.charge_type_code`

**Auto tags:** no longer runs, joins 2->3

**Category:** 

### 18. `world_1` (question #766)

**Question:** What is the total number of people living in the nations that do not use English?

**Gold:**
```sql
SELECT sum(Population) FROM country WHERE Name NOT IN (SELECT T1.Name FROM country AS T1 JOIN countrylanguage AS T2 ON T1.Code  =  T2.CountryCode WHERE T2.Language  =  "English")
```

**dev_zero_shot:**
```sql
SELECT SUM(Population) FROM country WHERE Code NOT IN ( SELECT CountryCode FROM countrylanguage WHERE Language = 'English' )
```

**dev_qlora_r16_final:**
```sql
SELECT sum(T1.Population) FROM country AS T1 JOIN countrylanguage AS T2 ON T1.Code  =  T2.CountryCode WHERE T2.Language != 'English'
```

**Auto tags:** joins 0->1, SELECTs 2->1 (subqueries/set ops), T1/T2 aliases added

**Category:** 

### 19. `network_1` (question #883)

**Question:** How many friends does each student have?

**Gold:**
```sql
SELECT student_id ,  count(*) FROM Friend GROUP BY student_id
```

**dev_zero_shot:**
```sql
SELECT student_id, COUNT(friend_id) as num_friends FROM Friend GROUP BY student_id
```

**dev_qlora_r16_final:**
```sql
SELECT count(*) FROM friend
```

**Auto tags:** GROUP BY removed

**Category:** 

### 20. `world_1` (question #748)

**Question:** What are the names of nations where both English and French are official languages?

**Gold:**
```sql
SELECT T1.Name FROM country AS T1 JOIN countrylanguage AS T2 ON T1.Code  =  T2.CountryCode WHERE T2.Language  =  "English" AND T2.IsOfficial  =  "T" INTERSECT SELECT T1.Name FROM country AS T1 JOIN countrylanguage AS T2 ON T1.Code  =  T2.CountryCode WHERE T2.Language  =  "French" AND T2.IsOfficial  =  "T"
```

**dev_zero_shot:**
```sql
SELECT T1.Name FROM country AS T1 JOIN countrylanguage AS T2 ON T1.Code = T2.CountryCode WHERE T2.Language = 'English' AND T2.IsOfficial = 'T' INTERSECT SELECT T1.Name FROM country AS T1 JOIN countrylanguage AS T2 ON T1.Code = T2.CountryCode WHERE T2.Language = 'French' AND T2.IsOfficial = 'T'
```

**dev_qlora_r16_final:**
```sql
SELECT T1.Name FROM country AS T1 JOIN countrylanguage AS T2 ON T1.Code  =  T2.CountryCode WHERE T2.IsOfficial  =  'Yes' AND T2.Language  =  'English' INTERSECT SELECT T1.Name FROM country AS T1 JOIN countrylanguage AS T2 ON T1.Code  =  T2.CountryCode WHERE T2.IsOfficial  =  'Yes' AND T2.Language  =  'French'
```

**Auto tags:** none

**Category:** 

### 21. `car_1` (question #161)

**Question:** How many countries has more than 2 car makers ?

**Gold:**
```sql
select count(*) from countries as t1 join car_makers as t2 on t1.countryid  =  t2.country group by t1.countryid having count(*)  >  2
```

**dev_zero_shot:**
```sql
SELECT COUNT(Country) FROM car_makers GROUP BY Country HAVING COUNT(Maker) > 2
```

**dev_qlora_r16_final:**
```sql
SELECT count(*) FROM (SELECT T1.Country FROM countries AS T1 JOIN car_makers AS T2 ON T1.CountryId  =  T2.Country GROUP BY T1.Country HAVING count(*)  >  2)
```

*Did not run:* `OperationalError: no such column: T1.Country`

**Auto tags:** no longer runs, joins 0->1, SELECTs 1->2 (subqueries/set ops), T1/T2 aliases added

**Category:** 

### 22. `cre_Doc_Template_Mgt` (question #335)

**Question:** What the smallest version number and its template type code?

**Gold:**
```sql
SELECT min(Version_Number) ,  template_type_code FROM Templates
```

**dev_zero_shot:**
```sql
SELECT MIN(Version_Number), Template_Type_Code FROM Templates
```

**dev_qlora_r16_final:**
```sql
SELECT min(version_Number) ,  template_type_code FROM Templates GROUP BY template_type_code
```

**Auto tags:** GROUP BY added

**Category:** 

### 23. `dog_kennels` (question #955)

**Question:** Which dogs are of the rarest breed? Show their names and treatment dates.

**Gold:**
```sql
SELECT T1.name ,  T2.date_of_treatment FROM Dogs AS T1 JOIN Treatments AS T2 ON T1.dog_id  =  T2.dog_id WHERE T1.breed_code  =  ( SELECT breed_code FROM Dogs GROUP BY breed_code ORDER BY count(*) ASC LIMIT 1 )
```

**dev_zero_shot:**
```sql
SELECT D.name, T.date_of_treatment FROM Dogs D JOIN Treatments T ON D.dog_id = T.dog_id WHERE D.breed_code IN (SELECT breed_code FROM Dogs GROUP BY breed_code ORDER BY COUNT(*) ASC LIMIT 1)
```

**dev_qlora_r16_final:**
```sql
SELECT T1.name ,  T3.date_of_treatment FROM dogs AS T1 JOIN breeds AS T2 ON T1.breed_code  =  T2.breed_code JOIN treatments AS T3 ON T1.dog_id  =  T3.dog_id WHERE T2.breed_name  =  (SELECT breed_name FROM breeds GROUP BY breed_name ORDER BY count(*) ASC LIMIT 1)
```

**Auto tags:** joins 1->2, T1/T2 aliases added

**Category:** 

### 24. `pets_1` (question #67)

**Question:** Find the type and weight of the youngest pet.

**Gold:**
```sql
SELECT pettype ,  weight FROM pets ORDER BY pet_age LIMIT 1
```

**dev_zero_shot:**
```sql
SELECT PetType, weight FROM Pets ORDER BY pet_age ASC LIMIT 1
```

**dev_qlora_r16_final:**
```sql
SELECT pet_type ,  weight FROM pets ORDER BY pet_age LIMIT 1
```

*Did not run:* `OperationalError: no such column: pet_type`

**Auto tags:** no longer runs

**Category:** 

### 25. `cre_Doc_Template_Mgt` (question #356)

**Question:** Return the ids corresponding to templates with the description 'Presentation'.

**Gold:**
```sql
SELECT T2.template_id FROM Ref_template_types AS T1 JOIN Templates AS T2 ON T1.template_type_code  = T2.template_type_code WHERE T1.template_type_description  =  "Presentation"
```

**dev_zero_shot:**
```sql
SELECT T1.Template_ID FROM Templates AS T1 INNER JOIN Ref_Template_Types AS T2 ON T1.Template_Type_Code = T2.Template_Type_Code WHERE T2.Template_Type_Description = 'Presentation'
```

**dev_qlora_r16_final:**
```sql
SELECT template_id FROM templates WHERE template_details  =  'Presentation'
```

**Auto tags:** joins 1->0, T1/T2 aliases removed

**Category:** 

### 26. `singer` (question #1027)

**Question:** What is the sname of every sing that does not have any song?

**Gold:**
```sql
SELECT Name FROM singer WHERE Singer_ID NOT IN (SELECT Singer_ID FROM song)
```

**dev_zero_shot:**
```sql
SELECT Name FROM singer WHERE Singer_ID NOT IN (SELECT Singer_ID FROM song)
```

**dev_qlora_r16_final:**
```sql
SELECT sname FROM singer EXCEPT SELECT T1.sname FROM singer AS T1 JOIN song AS T2 ON T1.Singer_ID  =  T2.Singer_ID
```

*Did not run:* `OperationalError: no such column: T1.sname`

**Auto tags:** no longer runs, joins 0->1, T1/T2 aliases added

**Category:** 

### 27. `dog_kennels` (question #997)

**Question:** Find the distinct breed type and size type combinations for dogs.

**Gold:**
```sql
SELECT DISTINCT breed_code ,  size_code FROM dogs
```

**dev_zero_shot:**
```sql
SELECT DISTINCT breed_code, size_code FROM Dogs
```

**dev_qlora_r16_final:**
```sql
SELECT DISTINCT breed_type ,  size_type FROM Dogs
```

*Did not run:* `OperationalError: no such column: breed_type`

**Auto tags:** no longer runs

**Category:** 

### 28. `battle_death` (question #499)

**Question:** What are the ids and names of the battles that led to more than 10 people killed in total.

**Gold:**
```sql
SELECT T1.id ,  T1.name FROM battle AS T1 JOIN ship AS T2 ON T1.id  =  T2.lost_in_battle JOIN death AS T3 ON T2.id  =  T3.caused_by_ship_id GROUP BY T1.id HAVING sum(T3.killed)  >  10
```

**dev_zero_shot:**
```sql
SELECT T1.id, T1.name FROM battle AS T1 JOIN ship AS T2 ON T1.id = T2.lost_in_battle JOIN death AS T3 ON T2.id = T3.caused_by_ship_id GROUP BY T1.id HAVING SUM(T3.killed) > 10
```

**dev_qlora_r16_final:**
```sql
SELECT T1.id ,  T1.name FROM battle AS T1 JOIN death AS T2 ON T1.id  =  T2.caused_by_ship_id GROUP BY T1.id HAVING sum(T2.killed)  >  10
```

**Auto tags:** joins 2->1

**Category:** 

### 29. `network_1` (question #914)

**Question:** Find the average grade of all students who have some friends.

**Gold:**
```sql
SELECT avg(grade) FROM Highschooler WHERE id IN (SELECT T1.student_id FROM Friend AS T1 JOIN Highschooler AS T2 ON T1.student_id  =  T2.id)
```

**dev_zero_shot:**
```sql
SELECT AVG(grade) FROM Highschooler WHERE ID IN (SELECT student_id FROM Friend)
```

**dev_qlora_r16_final:**
```sql
SELECT avg(T1.grade) FROM Highschooler AS T1 JOIN friend AS T2 ON T1.id  =  T2.student_id
```

**Auto tags:** joins 0->1, SELECTs 2->1 (subqueries/set ops), T1/T2 aliases added

**Category:** 

### 30. `world_1` (question #744)

**Question:** How many countries speak both English and Dutch?

**Gold:**
```sql
SELECT COUNT(*) FROM (SELECT T1.Name FROM country AS T1 JOIN countrylanguage AS T2 ON T1.Code  =  T2.CountryCode WHERE T2.Language  =  "English" INTERSECT SELECT T1.Name FROM country AS T1 JOIN countrylanguage AS T2 ON T1.Code  =  T2.CountryCode WHERE T2.Language  =  "Dutch")
```

**dev_zero_shot:**
```sql
SELECT COUNT(*) FROM countrylanguage WHERE Language = 'English' AND CountryCode IN (SELECT CountryCode FROM countrylanguage WHERE Language = 'Dutch')
```

**dev_qlora_r16_final:**
```sql
SELECT COUNT ( CountryCode ) FROM countrylanguage WHERE Language  =  "English" INTERSECT SELECT COUNT ( CountryCode ) FROM countrylanguage WHERE Language  =  "Dutch"
```

**Auto tags:** none

**Category:** 

### 31. `world_1` (question #769)

**Question:** What is the official language used in the country the name of whose head of state is Beatrix.

**Gold:**
```sql
SELECT T2.Language FROM country AS T1 JOIN countrylanguage AS T2 ON T1.Code  =  T2.CountryCode WHERE T1.HeadOfState  =  "Beatrix" AND T2.IsOfficial  =  "T"
```

**dev_zero_shot:**
```sql
SELECT T2.Language FROM country AS T1 INNER JOIN countrylanguage AS T2 ON T1.Code = T2.CountryCode WHERE T1.HeadOfState = 'Beatrix' AND T2.IsOfficial = 'T'
```

**dev_qlora_r16_final:**
```sql
SELECT T1.Language FROM countrylanguage AS T1 JOIN country AS T2 ON T1.CountryCode  =  T2.Code WHERE T2.HeadOfState  =  "Beatrix" AND T1.IsOfficial  =  "Yes"
```

**Auto tags:** none

**Category:** 

### 32. `cre_Doc_Template_Mgt` (question #345)

**Question:** Show all template type codes that are not used by any document.

**Gold:**
```sql
SELECT template_type_code FROM Templates EXCEPT SELECT template_type_code FROM Templates AS T1 JOIN Documents AS T2 ON T1.template_id  =  T2.template_id
```

**dev_zero_shot:**
```sql
SELECT Template_Type_Code FROM Ref_Template_Types WHERE Template_Type_Code NOT IN (SELECT Template_Type_Code FROM Templates WHERE Template_ID IN (SELECT Template_ID FROM Documents))
```

**dev_qlora_r16_final:**
```sql
SELECT template_type_code FROM templates EXCEPT SELECT template_type_code FROM documents
```

*Did not run:* `OperationalError: no such column: template_type_code`

**Auto tags:** no longer runs, SELECTs 3->2 (subqueries/set ops)

**Category:** 

### 33. `tvshow` (question #627)

**Question:** Find the number of cartoons directed by each of the listed directors.

**Gold:**
```sql
SELECT count(*) ,  Directed_by FROM cartoon GROUP BY Directed_by
```

**dev_zero_shot:**
```sql
SELECT Directed_by, COUNT(*) FROM Cartoon GROUP BY Directed_by
```

**dev_qlora_r16_final:**
```sql
SELECT COUNT(*) ,  directed_by FROM Cartoon WHERE directed_by  =  "Tim Johnson" OR directed_by  =  "John DiMaggio" OR directed_by  =  "Ken Hughes" OR directed_by  =  "Mike Judge" OR directed_by  =  "John Kricfalusi" GROUP BY directed_by
```

**Auto tags:** none

**Category:** 

### 34. `pets_1` (question #74)

**Question:** What is the average weight for each type of pet?

**Gold:**
```sql
SELECT avg(weight) ,  pettype FROM pets GROUP BY pettype
```

**dev_zero_shot:**
```sql
SELECT PetType, AVG(weight) FROM Pets GROUP BY PetType
```

**dev_qlora_r16_final:**
```sql
SELECT pet_type ,  avg(weight) FROM pets GROUP BY pet_type
```

*Did not run:* `OperationalError: no such column: pet_type`

**Auto tags:** no longer runs

**Category:** 

### 35. `student_transcripts_tracking` (question #512)

**Question:** What are the descriptions for all the math courses?

**Gold:**
```sql
SELECT course_description FROM Courses WHERE course_name  =  'math'
```

**dev_zero_shot:**
```sql
SELECT course_description FROM Courses WHERE course_name LIKE '%math%'
```

**dev_qlora_r16_final:**
```sql
SELECT course_description FROM courses WHERE course_name  =  "Math"
```

**Auto tags:** none

**Category:** 

### 36. `network_1` (question #901)

**Question:** What are the names of high schoolers who both have friends and are liked?

**Gold:**
```sql
SELECT T2.name FROM Friend AS T1 JOIN Highschooler AS T2 ON T1.student_id  =  T2.id INTERSECT SELECT T2.name FROM Likes AS T1 JOIN Highschooler AS T2 ON T1.liked_id  =  T2.id
```

**dev_zero_shot:**
```sql
SELECT name FROM Highschooler WHERE ID IN (SELECT student_id FROM Friend) AND ID IN (SELECT liked_id FROM Likes)
```

**dev_qlora_r16_final:**
```sql
SELECT T1.name FROM Highschooler AS T1 JOIN Likes AS T2 ON T1.id  =  T2.student_id INTERSECT SELECT T1.name FROM Highschooler AS T1 JOIN Friend AS T2 ON T1.id  =  T2.student_id
```

**Auto tags:** joins 0->2, SELECTs 3->2 (subqueries/set ops), T1/T2 aliases added

**Category:** 

### 37. `student_transcripts_tracking` (question #545)

**Question:** What are all the course names of the courses which ever have students enrolled in?

**Gold:**
```sql
SELECT DISTINCT T1.course_name FROM Courses AS T1 JOIN Student_Enrolment_Courses AS T2 ON T1.course_id  =  T2.course_id
```

**dev_zero_shot:**
```sql
SELECT DISTINCT T1.course_name FROM Courses AS T1 JOIN Student_Enrolment_Courses AS T2 ON T1.course_id = T2.course_id
```

**dev_qlora_r16_final:**
```sql
SELECT T1.course_name FROM Courses AS T1 JOIN Student_Enrolment_Courses AS T2 ON T1.course_id  =  T2.course_id
```

**Auto tags:** DISTINCT removed

**Category:** 

### 38. `pets_1` (question #73)

**Question:** Find the average weight for each pet type.

**Gold:**
```sql
SELECT avg(weight) ,  pettype FROM pets GROUP BY pettype
```

**dev_zero_shot:**
```sql
SELECT PetType, AVG(weight) FROM Pets GROUP BY PetType
```

**dev_qlora_r16_final:**
```sql
SELECT pet_type ,  avg(weight) FROM pets GROUP BY pet_type
```

*Did not run:* `OperationalError: no such column: pet_type`

**Auto tags:** no longer runs

**Category:** 

### 39. `world_1` (question #783)

**Question:** Return the codes of countries that do not speak English and do not have Republics for governments.

**Gold:**
```sql
SELECT Code FROM country WHERE GovernmentForm != "Republic" EXCEPT SELECT CountryCode FROM countrylanguage WHERE LANGUAGE  =  "English"
```

**dev_zero_shot:**
```sql
SELECT Code FROM country WHERE Code NOT IN ( SELECT CountryCode FROM countrylanguage WHERE Language = 'English' ) AND GovernmentForm != 'Republic'
```

**dev_qlora_r16_final:**
```sql
SELECT Code FROM country EXCEPT SELECT Code FROM countrylanguage WHERE Language  =  "English" UNION SELECT Code FROM country WHERE GovernmentForm  =  "Republic"
```

*Did not run:* `OperationalError: no such column: Code`

**Auto tags:** no longer runs, SELECTs 2->3 (subqueries/set ops)

**Category:** 

### 40. `world_1` (question #787)

**Question:** Return the different names of cities that are in Asia and for which Chinese is the official language.

**Gold:**
```sql
SELECT DISTINCT T3.Name FROM country AS T1 JOIN countrylanguage AS T2 ON T1.Code  =  T2.CountryCode JOIN city AS T3 ON T1.Code  =  T3.CountryCode WHERE T2.IsOfficial  =  'T' AND T2.Language  =  'Chinese' AND T1.Continent  =  "Asia"
```

**dev_zero_shot:**
```sql
SELECT DISTINCT T1.Name FROM city AS T1 JOIN country AS T2 ON T1.CountryCode = T2.Code JOIN countrylanguage AS T3 ON T2.Code = T3.CountryCode WHERE T2.Continent = 'Asia' AND T3.Language = 'Chinese' AND T3.IsOfficial = 'T'
```

**dev_qlora_r16_final:**
```sql
SELECT DISTINCT t1.name FROM city AS t1 JOIN country AS t2 ON t1.countrycode  =  t2.code JOIN countrylanguage AS t3 ON t2.code  =  t3.countrycode WHERE t2.continent  =  'Asia' AND t3.IsOfficial  =  'Yes' AND t3.Language  =  'Chinese'
```

**Auto tags:** none

**Category:** 

### 41. `student_transcripts_tracking` (question #546)

**Question:** What are the names of all courses that have some students enrolled?

**Gold:**
```sql
SELECT DISTINCT T1.course_name FROM Courses AS T1 JOIN Student_Enrolment_Courses AS T2 ON T1.course_id  =  T2.course_id
```

**dev_zero_shot:**
```sql
SELECT DISTINCT T1.course_name FROM Courses AS T1 JOIN Student_Enrolment_Courses AS T2 ON T1.course_id = T2.course_id
```

**dev_qlora_r16_final:**
```sql
SELECT T1.course_name FROM Courses AS T1 JOIN Student_Enrolment_Courses AS T2 ON T1.course_id  =  T2.course_id
```

**Auto tags:** DISTINCT removed

**Category:** 

### 42. `dog_kennels` (question #954)

**Question:** List the names of the dogs of the rarest breed and the treatment dates of them.

**Gold:**
```sql
SELECT T1.name ,  T2.date_of_treatment FROM Dogs AS T1 JOIN Treatments AS T2 ON T1.dog_id  =  T2.dog_id WHERE T1.breed_code  =  ( SELECT breed_code FROM Dogs GROUP BY breed_code ORDER BY count(*) ASC LIMIT 1 )
```

**dev_zero_shot:**
```sql
SELECT T1.name, T2.date_of_treatment FROM Dogs AS T1 INNER JOIN Treatments AS T2 ON T1.dog_id = T2.dog_id WHERE T1.breed_code = ( SELECT breed_code FROM Dogs GROUP BY breed_code ORDER BY count(*) ASC LIMIT 1 )
```

**dev_qlora_r16_final:**
```sql
SELECT T1.name ,  T2.date_of_treatment FROM Dogs AS T1 JOIN Treatments AS T2 ON T1.dog_id  =  T2.dog_id JOIN Breeds AS T3 ON T1.breed_code  =  T3.breed_code WHERE T3.breed_name  =  (SELECT breed_name FROM Breeds GROUP BY breed_name ORDER BY count(*) ASC LIMIT 1)
```

**Auto tags:** joins 1->2

**Category:** 

### 43. `pets_1` (question #72)

**Question:** What is the average and maximum age for each pet type?

**Gold:**
```sql
SELECT avg(pet_age) ,  max(pet_age) ,  pettype FROM pets GROUP BY pettype
```

**dev_zero_shot:**
```sql
SELECT PetType, AVG(pet_age) AS avg_age, MAX(pet_age) AS max_age FROM Pets GROUP BY PetType
```

**dev_qlora_r16_final:**
```sql
SELECT pet_type ,  avg(pet_age) ,  max(pet_age) FROM pets GROUP BY pet_type
```

*Did not run:* `OperationalError: no such column: pet_type`

**Auto tags:** no longer runs

**Category:** 

### 44. `world_1` (question #751)

**Question:** How many continents speak Chinese?

**Gold:**
```sql
SELECT COUNT( DISTINCT Continent) FROM country AS T1 JOIN countrylanguage AS T2 ON T1.Code  =  T2.CountryCode WHERE T2.Language  =  "Chinese"
```

**dev_zero_shot:**
```sql
SELECT COUNT(DISTINCT T1.Continent) FROM country AS T1 INNER JOIN countrylanguage AS T2 ON T1.Code = T2.CountryCode WHERE T2.Language = 'Chinese'
```

**dev_qlora_r16_final:**
```sql
SELECT COUNT ( DISTINCT t1.continent ) FROM country AS t1 JOIN countrylanguage AS t2 ON t1.code  =  t2.countrycode WHERE t2.language  =  'Chinese' AND t2.IsOfficial  =  'Yes'
```

**Auto tags:** none

**Category:** 

### 45. `network_1` (question #900)

**Question:** Show name of all students who have some friends and also are liked by someone else.

**Gold:**
```sql
SELECT T2.name FROM Friend AS T1 JOIN Highschooler AS T2 ON T1.student_id  =  T2.id INTERSECT SELECT T2.name FROM Likes AS T1 JOIN Highschooler AS T2 ON T1.liked_id  =  T2.id
```

**dev_zero_shot:**
```sql
SELECT name FROM Highschooler WHERE ID IN (SELECT student_id FROM Friend) AND ID IN (SELECT liked_id FROM Likes)
```

**dev_qlora_r16_final:**
```sql
SELECT T1.name FROM Highschooler AS T1 JOIN Friend AS T2 ON T1.id  =  T2.student_id INTERSECT SELECT T3.name FROM Highschooler AS T3 JOIN Likes AS T4 ON T3.id  =  T4.student_id
```

**Auto tags:** joins 0->2, SELECTs 3->2 (subqueries/set ops), T1/T2 aliases added

**Category:** 

### 46. `car_1` (question #103)

**Question:** Which distinct car models are the produced after 1980?

**Gold:**
```sql
SELECT DISTINCT T1.model FROM MODEL_LIST AS T1 JOIN CAR_NAMES AS T2 ON T1.model  =  T2.model JOIN CARS_DATA AS T3 ON T2.MakeId  =  T3.id WHERE T3.year  >  1980;
```

**dev_zero_shot:**
```sql
SELECT DISTINCT T1.Model FROM model_list AS T1 INNER JOIN car_names AS T2 ON T1.Model = T2.Model WHERE T2.MakeId IN ( SELECT Id FROM cars_data WHERE Year > 1980 )
```

**dev_qlora_r16_final:**
```sql
SELECT DISTINCT T1.Model FROM model_list AS T1 JOIN car_names AS T2 ON T1.Model  =  T2.Model WHERE T2.Year  >  1980
```

*Did not run:* `OperationalError: no such column: T2.Year`

**Auto tags:** no longer runs, SELECTs 2->1 (subqueries/set ops)

**Category:** 

### 47. `cre_Doc_Template_Mgt` (question #373)

**Question:** What is the document id and name with greatest number of paragraphs?

**Gold:**
```sql
SELECT T1.document_id ,  T2.document_name FROM Paragraphs AS T1 JOIN Documents AS T2 ON T1.document_id  =  T2.document_id GROUP BY T1.document_id ORDER BY count(*) DESC LIMIT 1
```

**dev_zero_shot:**
```sql
SELECT T1.Document_ID, T1.Document_Name FROM Documents AS T1 JOIN Paragraphs AS T2 ON T1.Document_ID = T2.Document_ID GROUP BY T1.Document_ID, T1.Document_Name ORDER BY COUNT(T2.Paragraph_ID) DESC LIMIT 1
```

**dev_qlora_r16_final:**
```sql
SELECT T1.document_id ,  T2.document_name FROM Documents AS T1 JOIN Documents AS T2 ON T1.document_id  =  T2.document_id GROUP BY T1.document_id ORDER BY count(*) DESC LIMIT 1
```

**Auto tags:** none

**Category:** 
