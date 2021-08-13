--name database bitland

--
--BITLAND SCHEMA
--
create extension postgis;
create schema bitland;

drop table if exists bitland.planet cascade;
create table bitland.planet (
  id SERIAL PRIMARY key,
  name varchar
 );

insert into bitland.planet (id, name) values 
(1, 'earth'), (2, 'mars');

drop table if exists bitland.block cascade;
create table bitland.block (
  id int primary key, 
  header_hash varchar,
  version bigint,
  prev_block varchar, 
  mrkl_root varchar,
  time bigint,
  bits bigint,
  bitcoin_block_height bigint,
  miner_bitcoin_address varchar,
  nonce bigint
 );

insert into bitland.block(id, header_hash) values
(0, '0000000000000000000000000000000000000000000000000000000000000000');

drop table if exists bitland.transaction cascade;
create table bitland.transaction (
  id SERIAL PRIMARY key, 
  block_id int, 
  transaction_hash varchar,
  version int,
  is_landbase bool,
  miner_fee_sats int,
  miner_fee_blocks int, 
  transfer_fee_sats int, 
  transfer_fee_blocks int,
  transfer_fee_address varchar,
  CONSTRAINT transaction_block_id_fkey FOREIGN KEY (block_id) REFERENCES bitland.block(id)
 );
--select * from bitland.transaction

drop table if exists bitland.output_parcel cascade;
create table bitland.output_parcel (
  id SERIAL PRIMARY key,
  transaction_id int,
  output_version int, 
  pub_key varchar,
  vout int, 
  planet_id int,
  geom geometry,
  CONSTRAINT output_transaction_id_fkey FOREIGN KEY (transaction_id) REFERENCES bitland.transaction(id)
 );

CREATE INDEX idx_output_parcel_geom_gist ON bitland.output_parcel USING gist (geom);

drop table if exists bitland.input_parcel cascade;
create table bitland.input_parcel (
  id SERIAL PRIMARY key,
  transaction_id int,
  vin int,
  input_version int,
  input_transaction_hash varchar,
  input_transaction_id int,
  vout int,
  output_parcel_id int,
  sig varchar,
  CONSTRAINT input_transaction_id_fkey FOREIGN KEY (transaction_id) REFERENCES bitland.transaction(id),
  CONSTRAINT input_output_transaction_id_fkey FOREIGN KEY (input_transaction_id) REFERENCES bitland.transaction(id),
  CONSTRAINT input_output_parcel_id_fkey FOREIGN KEY (output_parcel_id) REFERENCES bitland.output_parcel(id)
 );
 
drop table if exists bitland.claim cascade;
create table bitland.claim(
  id SERIAL primary key, 
  claimed_output_parcel_id int, 
  claim_action_output_parcel_id int,
  claim_fee_sats int,
  claim_block_height int,
  invalidation_input_parcel_id int,
  status varchar,
  claim_end_block int,
  from_bitland_block_height int,
  to_bitland_block_height int,
  CONSTRAINT claimed_output_parcel_id_fkey FOREIGN KEY (claimed_output_parcel_id) REFERENCES bitland.output_parcel(id),
  CONSTRAINT claim_action_output_parcel_id_fkey FOREIGN KEY (claim_action_output_parcel_id) REFERENCES bitland.output_parcel(id),
  CONSTRAINT claim_block_height_fkey FOREIGN KEY (claim_block_height) REFERENCES bitland.block(id)
);

drop table if exists bitland.miner_fee_transaction cascade;
create table bitland.miner_fee_transaction(
  id  SERIAL primary key, 
  transaction_id int, 
  bitcoin_block_height int,
  bitcoin_transaction_hash varchar, 
  bitcoin_address varchar, 
  sats int,
  status varchar,
  bitland_block_height int,
  CONSTRAINT miner_fee_transaction_id_fkey FOREIGN KEY (transaction_id) REFERENCES bitland.transaction(id)
);

drop table if exists bitland.transfer_fee_transaction cascade;
create table bitland.transfer_fee_transaction(
  id SERIAL primary key, 
  transaction_id int, 
  bitcoin_block_height int,
  bitcoin_transaction_hash varchar, 
  bitcoin_address varchar, 
  sats int,
  status varchar,
  bitland_block_height int,
  CONSTRAINT transfer_fee_transaction_id_fkey FOREIGN KEY (transaction_id) REFERENCES bitland.transaction(id)
);


--
--BITCOIN SCHEMA
--
create schema bitcoin;

drop table if exists bitcoin.recent_transactions;
create table bitcoin.recent_transactions(bitcoin_block_height int, address varchar, value float8, txid varchar);

drop table if exists bitcoin.relevant_contingency_transaction;
create table bitcoin.relevant_contingency_transaction (bitcoin_block_height int, address varchar, value float8, txid varchar, recorded_bitland_block_height int);

drop table if exists bitcoin.block;
create table bitcoin.block(block_height int, block_hash varchar);


--
--NETWORKING SCHEMA
--
create schema networking;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

drop table if exists networking.peer;
create table networking.peer (
  ip_address varchar,
  port int,
  status varchar,
  connected_time time default now(),
  last_ping time default now(),
  self_auth_key uuid,
  peer_auth_key uuid default uuid_generate_v1() 
);
  
drop table if exists bitland.transaction_mempool cascade;
create table bitland.transaction_mempool (
  id SERIAL PRIMARY key, 
  transaction_hash varchar,
  version int,
  is_landbase bool,
  miner_fee_sats int,
  miner_fee_blocks int, 
  transfer_fee_sats int, 
  transfer_fee_blocks int,
  transfer_fee_address varchar,
  transaction_serialized varchar,
  byte_size int  
 );


--
--INITIALIZING DATA
--
drop table if exists bitland.geography_definition;
create table bitland.geography_definition(id serial PRIMARY key, x_split int, y_count int, start_y_ratio float8, y_ratio_increase float8);
insert into bitland.geography_definition (x_split , y_count , start_y_ratio , y_ratio_increase) values 
(4,1,0,0),
(8,1,0,0),
(16,2,0.33,0.66),
(32,4,0.3,0.2),
(64,8,0.35,0.1),
(128,16,0.3,0.04),
(256,32,0.31,0.02),
(512,64,0.315,0.01),
(1024,128,0.3175,0.005),
(2048,256,0.159375,0.00125),
(2048,256,0.159375,0.00125),
(1024,128,0.3175,0.005),
(512,64,0.315,0.01),
(256,32,0.31,0.02),
(128,16,0.3,0.04),
(64,8,0.35,0.1),
(32,4,0.3,0.2),
(16,2,0.33,0.66),
(8,1,0,0),
(4,1,0,0);


drop table if exists bitland.int_join;
create table bitland.int_join (id serial primary key, a int);

insert into bitland.int_join (a) values (1);
insert into bitland.int_join (a) select a from bitland.int_join;
insert into bitland.int_join (a) select a from bitland.int_join;
insert into bitland.int_join (a) select a from bitland.int_join;
insert into bitland.int_join (a) select a from bitland.int_join;
insert into bitland.int_join (a) select a from bitland.int_join;
insert into bitland.int_join (a) select a from bitland.int_join;
insert into bitland.int_join (a) select a from bitland.int_join;
insert into bitland.int_join (a) select a from bitland.int_join;
insert into bitland.int_join (a) select a from bitland.int_join;
insert into bitland.int_join (a) select a from bitland.int_join;
insert into bitland.int_join (a) select a from bitland.int_join;
insert into bitland.int_join (a) select a from bitland.int_join;


--drop table if exists bitland.tiles;
--create table bitland.tiles (id serial primary key, x_ordinal int, y_ordinal int, x float8, y float8, geom_1024 geometry, geom_4386 geometry);

with calc1 as (
select g.*, i.id as y_level, i2.id x_level, 1 + start_y_ratio - y_ratio_increase * (i.id - 1) as y_length, 2048 / x_split as x_length, (2048 / x_split)*(i2.id - 1) as x_start 
from bitland.geography_definition g
join bitland.int_join i on g.y_count >= i.id
join bitland.int_join i2 on g.x_split >= i2.id
where g.id <= 4
)
, cumulative_count as (
select g.id, coalesce(sum(g1.y_count),0) as cumulative_y_count 
from bitland.geography_definition g
left join bitland.geography_definition g1 on g.id > g1.id
group by 1
)
select * --x_level, y_level, x_start_, cumulative_y_count + x_length, 
from calc1 c1
join cumulative_count cc on c1.id = cc.id;

create schema testing;

drop table if exists testing.land_divide;
create table testing.land_divide (
	row int, 
	cols int, 
	x1 float8, 
	y1 float8, 
	x2 float8, 
	y2 float8, 
	x3 float8, 
	y3 float8, 
	x4 float8, 
	y4 float8, 
	long1 float8, 
	lat1 float8, 
	long2 float8, 
	lat2 float8, 
	long3 float8, 
	lat3 float8, 
	long4 float8, 
	lat4 float8,
	geom geometry,
	area float8,
	pt1 geometry,
	pt2 geometry,
	pt3 geometry
);

drop function if exists testing.find_polygons ();

create function testing.find_polygons ()
returns int
language plpgsql
as
$$
declare
   row_id integer := 1;
  	polygon_area float8;
  y_increase float8 := 0.00001;
 	iter int := 0;
 	x_split int := 4;
 	height float8 := 0;
 	width float8 := 0;
 	y_start float8 := 0;
 	y_plus float8 := 0.001;
 	y_start_prev float8 := 0;
 	diff float8 := 0;
 	target_area int := 400000000;
 	percent_diff float8 := 0;
 	min_count int := 0;
 	min_value float8 := 0;
begin

	loop
		
		exit when  y_start > .5; --row_id >= 10 ; y_start > .5;
		raise notice 'row_id %, y_start %', row_id, y_start; 	
		
		/*
		if (width > 1.5* height) then 
			x_split :=  x_split * 2;
			raise notice 'outer increasing x, row %, height %, width %', row_id, height, width;
		end if;
		*/
	
		insert into testing.land_divide(row,cols,x1 , y1 , x2 , y2 , x3 , y3 , x4 , y4   ) values
		(row_id, x_split,	0,	y_start,	0,	y_start + y_plus,	1/x_split::float8	,y_start + y_plus,	1/x_split::float8,y_start);
		
		update testing.land_divide set long1 = x1*360, lat1 = 90 - (y1*180), long2 = x2*360, lat2 = 90 - (y2*180), long3 = x3*360, lat3 = 90 - (y3*180), long4 = x4*360, lat4 = 90 - (y4*180) where row = row_id;
		update testing.land_divide set geom = st_geomfromtext('POLYGON((' ||long1 || ' ' ||lat1 || ',' ||long2 || ' ' ||lat2 || ',' ||long3 || ' ' ||lat3 || ',' ||long4 || ' ' ||lat4 || ',' ||long1 || ' ' ||lat1 || '))',4326 ) where row = row_id;
		update testing.land_divide set area = st_area(geom::geography) where row = row_id;
				
		update testing.land_divide set pt1 = st_geomfromtext('POINT (' || long1 || ' ' || lat1 || ')') where row = row_id; 
		update testing.land_divide set pt2 = st_geomfromtext('POINT (' || long2 || ' ' || lat2 || ')') where row = row_id;
		update testing.land_divide set pt3 = st_geomfromtext('POINT (' || long3 || ' ' || lat3 || ')') where row = row_id;
	
		select st_distance(pt1::geography, pt2::geography) into height from testing.land_divide where row = row_id;
		select st_distance(pt2::geography, pt3::geography) into width from testing.land_divide where row = row_id;
	
		select ld.area into polygon_area from testing.land_divide ld where row = row_id;
		
		raise notice 'starting loop for row %, area is %', row_id, polygon_area; 
		
		iter := 1;
		diff := 0;
		min_count := 0;
		min_value := 9999999999;
		if polygon_area - target_area < 0 then
			y_increase := 0.001;
		else
			y_increase := -0.001;
		end if;
	
		loop 
			--raise notice 'min_count %, min_value %, y_increase %', min_count, min_value, y_increase;
			exit when (abs (y_increase) = 0.000001 and min_count = 3); --polygon_area > 400000000;
			diff := polygon_area - target_area;
			percent_diff := polygon_area / target_area;
		
			--split horizontal if width > 2* height
			if ( (percent_diff between 0.9 and 1) and width > 2* height) then 
				x_split :=  x_split * 2;
				update testing.land_divide set cols = x_split, x3 = 1/x_split::float8, x4 = 1/x_split::float8, y2 = (y2 - y_start) * 2 + y_start, y3 = (y3 - y_start) * 2 + y_start where row = row_id;
				update testing.land_divide set long1 = x1*360, lat1 = 90 - (y1*180), long2 = x2*360, lat2 = 90 - (y2*180), long3 = x3*360, lat3 = 90 - (y3*180), long4 = x4*360, lat4 = 90 - (y4*180) where row = row_id;
				update testing.land_divide set geom = st_geomfromtext('POLYGON((' ||long1 || ' ' ||lat1 || ',' ||long2 || ' ' ||lat2 || ',' ||long3 || ' ' ||lat3 || ',' ||long4 || ' ' ||lat4 || ',' ||long1 || ' ' ||lat1 || '))',4326 ) where row = row_id;
				update testing.land_divide set area = st_area(geom::geography) where row = row_id;
				raise notice 'inner increasing x, row %, height %, width %', row_id, height, width;
				y_increase := y_increase *10;
				min_count := 0;
				min_value := 9999999999;
			end if;
			
			--update values
			update testing.land_divide set y2 = round((y2 + y_increase)::numeric,6), y3 = round((y3 + y_increase)::numeric,6) where row = row_id;
			update testing.land_divide set lat2 = 90 - (y2*180), lat3 = 90 - (y3*180) where row = row_id;
			update testing.land_divide set geom = st_geomfromtext('POLYGON((' ||long1 || ' ' ||lat1 || ',' ||long2 || ' ' ||lat2 || ',' ||long3 || ' ' ||lat3 || ',' ||long4 || ' ' ||lat4 || ',' ||long1 || ' ' ||lat1 || '))',4326 ) where row = row_id;
			update testing.land_divide set area = st_area(geom::geography) where row = row_id;
			update testing.land_divide set pt1 = st_geomfromtext('POINT (' || long1 || ' ' || lat1 || ')') where row = row_id; 
			update testing.land_divide set pt2 = st_geomfromtext('POINT (' || long2 || ' ' || lat2 || ')') where row = row_id;
			update testing.land_divide set pt3 = st_geomfromtext('POINT (' || long3 || ' ' || lat3 || ')') where row = row_id;
			select st_distance(pt1::geography, pt2::geography) into height from testing.land_divide where row = row_id;
			select st_distance(pt2::geography, pt3::geography) into width from testing.land_divide where row = row_id;
			select ld.area into polygon_area from testing.land_divide ld where row = row_id;
			raise notice 'row %, iter %, y_increase %, area %, height %, width %, signdiff %, signnewdiff %', row_id, iter, y_increase, polygon_area, height, width, sign(diff), sign(polygon_area - target_area); 
		
			if sign(diff) <> sign(polygon_area - target_area) then
				raise notice 'y+increase %', y_increase;
				--raise notice '%', abs(y_increase*0.1);
				--raise notice '%', abs(0.000001::float8);
				--raise notice '%', greatest(abs(y_increase*0.1), 0.000001::float8);
				y_increase := sign(y_increase) * -1 * (greatest(abs(y_increase*0.1), 0.000001::float8));
				raise notice 'y+increase %', y_increase;
			end if;
		
			--raise notice 'current difference %', abs(polygon_area - target_area) ;
			if abs(polygon_area - target_area) = min_value then
				min_count = min_count + 1;
			elsif abs(polygon_area - target_area) < min_value then
				min_count = 0;
				min_value = abs(polygon_area - target_area);
			end if;
				
			iter := iter + 1;
		
		end loop;
	
		raise notice 'loop ended for row %, area is %, lat1 is %, lat 2 is %, lat 3 is %', row_id, polygon_area, (select lat1 from testing.land_divide where row = row_id), (select lat2 from testing.land_divide where row = row_id), (select lat3 from testing.land_divide where row = row_id); 
		raise notice 'row %, iter %, area %, height %, width %', row_id, iter, polygon_area, height, width;
	
		update testing.land_divide set pt1 = st_geomfromtext('POINT (' || long1 || ' ' || lat1 || ')') where row = row_id; 
		update testing.land_divide set pt2 = st_geomfromtext('POINT (' || long2 || ' ' || lat2 || ')') where row = row_id;
		update testing.land_divide set pt3 = st_geomfromtext('POINT (' || long3 || ' ' || lat3 || ')') where row = row_id;
		
		select st_distance(pt1::geography, pt2::geography) into height from testing.land_divide where row = row_id;
		select st_distance(pt2::geography, pt3::geography) into width from testing.land_divide where row = row_id;
		y_start_prev := y_start;
		select ld.y2 into y_start from testing.land_divide ld where row = row_id;
		y_plus = y_start - y_start_prev;
		
		row_id := row_id + 1;
	
	end loop; 

	return row_id;
end;
$$;

truncate testing.land_divide;
select testing.find_polygons();

/*
select *,
  st_distance(pt1::geography, pt2::geography) as height,
  st_distance(pt2::geography, pt3::geography) as width
 from testing.land_divide
order by row;

select count(*)
from testing.land_divide
*/

--drop table testing.land_divide_test1
--select * into testing.land_divide_test1 from testing.land_divide;

update testing.land_divide
set y2 = 1-y1, y3 = 1-y1
where row = 488;

insert into testing.land_divide(row,cols,x1 , y1 , x2 , y2 , x3 , y3 , x4 , y4   ) 
select 488 + (488-row), cols, x1, 1-y1, x2, 1-y2, x3, 1-y3, x4, 1-y4
from testing.land_divide
where row <> 488
order by 488 + (488-row);

update testing.land_divide set geom = st_geomfromtext('POLYGON((' ||long1 || ' ' ||lat1 || ',' ||long2 || ' ' ||lat2 || ',' ||long3 || ' ' ||lat3 || ',' ||long4 || ' ' ||lat4 || ',' ||long1 || ' ' ||lat1 || '))',4326 );
update testing.land_divide set long1 = x1*360, lat1 = 90 - (y1*180), long2 = x2*360, lat2 = 90 - (y2*180), long3 = x3*360, lat3 = 90 - (y3*180), long4 = x4*360, lat4 = 90 - (y4*180);
update testing.land_divide set area = st_area(geom::geography);
		
update testing.land_divide set pt1 = st_geomfromtext('POINT (' || long1 || ' ' || lat1 || ')'); 
update testing.land_divide set pt2 = st_geomfromtext('POINT (' || long2 || ' ' || lat2 || ')');
update testing.land_divide set pt3 = st_geomfromtext('POINT (' || long3 || ' ' || lat3 || ')');

create table testing.iteration_table (id int);

drop function if exists testing.create_iteration_table ();

create function testing.create_iteration_table ()
returns int
language plpgsql
as
$$
declare
   row_count int := 2048;
 	iter int := 1;
begin

	loop
		
		exit when  iter > row_count; 
		insert into testing.iteration_table (id) values (iter);
		iter := iter + 1;
	
	end loop; 

	return iter;
end;
$$;

select testing.create_iteration_table();

create table bitland.landbase_enum(
	id serial PRIMARY key, 
	x_id int, 
	y_id int, 	
	x1 float8, 
	y1 float8, 
	x2 float8, 
	y2 float8, 
	x3 float8, 
	y3 float8, 
	x4 float8, 
	y4 float8, 
	long1 float8, 
	lat1 float8, 
	long2 float8, 
	lat2 float8, 
	long3 float8, 
	lat3 float8, 
	long4 float8, 
	lat4 float8,
	geom geometry,
	area float8);

CREATE INDEX idx_landbase_enum_geom_gist ON bitland.landbase_enum USING gist (geom);

insert into bitland.landbase_enum (x_id,y_id,x1 , y1 , x2 , y2 , x3 , y3 , x4 , y4 )
select itx.id as x_id, ity.id as y_id, 1/ld.cols::numeric*(itx.id-1) as x1, y1, 1/ld.cols::numeric*(itx.id-1) as x2, y2, 1/ld.cols::numeric*itx.id as x3, y3, 1/ld.cols::numeric*itx.id as x4, y4
from testing.land_divide ld 
join testing.iteration_table itx on ld.cols >= itx.id
join testing.iteration_table ity on ld.row = ity.id
order by y_id, x_id;


update bitland.landbase_enum set long1 = round((180 - x1*360)::numeric,6), lat1 = round((90 - (y1*180))::numeric,6), long2 = round((180 - x2*360)::numeric,6), 
	lat2 = round((90 - (y2*180))::numeric,6), long3 = round((180 - x3*360)::numeric,6), lat3 = round((90 - (y3*180))::numeric,6), 
	long4 = round((180 - x4*360)::numeric,6), lat4 = round((90 - (y4*180))::numeric,6);
update bitland.landbase_enum set geom = st_geomfromtext('POLYGON((' ||long1 || ' ' ||lat1 || ',' ||long2 || ' ' ||lat2 || ',' ||long3 || ' ' ||lat3 || ',' ||long4 || ' ' ||lat4 || ',' ||long1 || ' ' ||lat1 || '))',4326 ) ;
update bitland.landbase_enum set area = st_area(geom::geography) ;

alter table bitland.landbase_enum drop column long1;
alter table bitland.landbase_enum drop column long2;
alter table bitland.landbase_enum drop column long3;
alter table bitland.landbase_enum drop column long4;
alter table bitland.landbase_enum drop column lat1;
alter table bitland.landbase_enum drop column lat2;
alter table bitland.landbase_enum drop column lat3;
alter table bitland.landbase_enum drop column lat4;

alter table bitland.landbase_enum add column geom_x_y geometry;

update bitland.landbase_enum set geom_x_y = st_geomfromtext('POLYGON((' ||x1 || ' ' ||y1 || ',' ||x2|| ' ' ||y2 || ',' ||x3 || ' ' ||y3 || ',' ||x4 || ' ' ||y4|| ',' ||x1|| ' ' ||y1|| '))',4326 );

--select as_kmldoc(geom) from bitland.landbase_enum where y_id <= 8;

alter table bitland.landbase_enum add column block_claim int;

alter table bitland.landbase_enum add column valid_claim boolean;
update bitland.landbase_enum set valid_claim = false;

alter table bitland.landbase_enum add column valid_enabled_block int;

with minmax as (
select min(y_id) as min_id, max(y_id) as max_id
from bitland.landbase_enum le 
)
update bitland.landbase_enum le
set valid_claim = true
from minmax mm 
where le.y_id in (min_id, max_id);

create schema wallet;
create table wallet.addresses (private_key varchar, public_key varchar);

drop table if exists bitland.block_serialized ;
create table bitland.block_serialized (id int, block varchar);

insert into bitland.block_serialized(id, block) values
(0, '0000000000000000000000000000000000000000000000000000000000000000');


drop table bitland.int_join;
drop table bitland.geography_definition;
drop table if exists bitland.address;


--
--VIEWS AND FUNCTIONS
--

drop function if exists bitland.rollback_block (rollback_block_id int);
create function bitland.rollback_block (rollback_block_id int)
returns int
language plpgsql
as
$$
declare

begin

	with delete_block as (
	select $1 as block_id
	)
	, block_joins as (
	select distinct b.id as block_id, t.id as transaction_id, op.id as output_parcel_id, ip.id as input_parcel_id
	from bitland.block b
	join delete_block db on b.id = db.block_id
	left join bitland.transaction t on b.id = t.block_id 
	left join bitland.output_parcel op on t.id = op.transaction_id 
	left join bitland.input_parcel ip on t.id = ip.transaction_id
	)
	,delete_input_parceL as (
	delete from bitland.input_parcel 
	where id in (select distinct input_parcel_id from block_joins bj)
	)
	,delete_ouput_parceL as (
	delete from bitland.output_parcel 
	where id in (select distinct output_parcel_id from block_joins bj)
	)
	,delete_transaction as (
	delete from bitland.transaction
	where id in (select distinct transaction_id from block_joins bj)
	)
	--,delete_claim as (
	--delete from bitland.claim
	--where claim_block_height = $1
	--)
	,delete_claim_smd as (
	delete from bitland.claim
	where from_bitland_block_height = $1
	)
	,update_claim_smd as (
	update bitland.claim
	set to_bitland_block_height = null
	where to_bitland_block_height = $1
	)
	,delete_block_entry as (
	delete from bitland.block
	where id in (select distinct block_id from delete_block)
	)
	,delete_serialized_block as (
	delete from bitland.block_serialized
	where id in (select distinct block_id from delete_block)
	)
	,reset_landbase_enum as (
	update bitland.landbase_enum le
	set valid_claim = false, valid_enabled_block = null
	where valid_enabled_block in (select distinct block_id from delete_block)
	)
	update bitland.landbase_enum le
	set valid_claim = true, block_claim = null
	where block_claim in (select distinct block_id from delete_block);

	return $1;
end;
$$;


drop view if exists bitland.utxo;
create view bitland.utxo as 
select op.*, t.transaction_hash, t.block_id, t.miner_fee_sats, t.miner_fee_blocks, t.transfer_fee_sats, t.transfer_fee_blocks, t.transfer_fee_address, b.bitcoin_block_height, b.miner_bitcoin_address, opl.pub_key as miner_landbase_address, ipop.pub_key as transfer_fee_failover_address, c.claim_fee_sats, c.claim_block_height, mft.status as miner_fee_status, tft.status as transfer_fee_status, mft.bitcoin_block_height as miner_fee_status_block_height, tft.bitcoin_block_height as transfer_fee_status_block_height
from bitland.output_parcel op
left join bitland.input_parcel ip on op.id = ip.output_parcel_id and ip.input_version = 1
join bitland.transaction t on op.transaction_id = t.id
join bitland.block b on t.block_id = b.id
left join bitland.transaction tl on b.id = tl.block_id and tl.is_landbase = true
left join bitland.output_parcel opl on tl.id = opl.transaction_id
left join bitland.input_parcel ip2 on ip2.transaction_id = op.transaction_id and ip2.vin = 0
left join bitland.output_parcel ipop on ip2.output_parcel_id = ipop.id
left join bitland.claim c on c.claimed_output_parcel_id = op.id and c.to_bitland_block_height is null
left join bitland.miner_fee_transaction mft on op.transaction_id = mft.transaction_id
left join bitland.transfer_fee_transaction tft on op.transaction_id = tft.transaction_id
where ip.id is null;

drop view if exists bitland.transaction_contingency;
create view bitland.transaction_contingency as 
select t.*, b.bitcoin_block_height, mft.status as miner_fee_status, tft.status as transfer_fee_status, 
mft.bitcoin_block_height as miner_fee_status_block_height, 
tft.bitcoin_block_height as transfer_fee_status_block_height,
b.miner_bitcoin_address 
from bitland.transaction t
left join bitland.miner_fee_transaction mft on t.id = mft.transaction_id 
left join bitland.transfer_fee_transaction tft on t.id = tft.transaction_id
join bitland.block b on t.block_id = b.id;

drop view if exists bitland.vw_contingency_status;
create view bitland.vw_contingency_status as (
select 
  ct.*, 
  rct.bitcoin_block_height as validation_bitcoin_block_height, 
  rct.address as validation_address, 
  rct.value as validation_value, 
  rct.txid as validation_txid, 
  rct.recorded_bitland_block_height as validation_recorded_bitland_block_height
from 
(select t.id, t.transaction_hash, 'miner_fee' as type, b.miner_bitcoin_address as bitcoin_address, miner_fee_sats as fee_sats, miner_fee_blocks as fee_blocks, t.block_id as bitland_block, b.bitcoin_block_height, b.bitcoin_block_height + miner_fee_blocks as bitcoin_expiration_height
from bitland.transaction t
join bitland.block b on t.block_id = b.id
where miner_fee_sats > 0 
union 
select t.id, t.transaction_hash, 'transfer_fee' as type, transfer_fee_address as bitcoin_address, transfer_fee_sats as fee_sats, transfer_fee_blocks as fee_blocks, t.block_id as bitland_block, b.bitcoin_block_height, b.bitcoin_block_height + transfer_fee_blocks as bitcoin_expiration_height
from bitland.transaction t
join bitland.block b on t.block_id = b.id
where transfer_fee_sats > 0) ct 
left join bitcoin.relevant_contingency_transaction rct on ct.bitcoin_address = rct.address and ct.fee_sats = rct.value and rct.bitcoin_block_height > ct.bitcoin_block_height and rct.bitcoin_block_height <= ct.bitcoin_expiration_height
);

drop view if exists bitland.max_block;
create view bitland.max_block as
select coalesce(max(id),0) as max_block
from bitland.block;

drop function if exists bitland.update_expired_claims (bitcoin_block_height int, confirmation_blocks int, bitland_block_height int);
create function bitland.update_expired_claims (bitcoin_block_height int, confirmation_blocks int, bitland_block_height int)
returns int
language plpgsql
as
$$
declare

begin

	with expired as (
	select c.id
	from bitland.claim c
	join bitland.output_parcel op on c.claim_action_output_parcel_id = op.id
	  and c.status in ('OPEN')
	join bitland.vw_contingency_status vcs on op.transaction_id = vcs.id
	  and vcs.bitcoin_expiration_height < $1 + $2
	  and vcs.validation_bitcoin_block_height is null
	),
	insert_new_record as (
	insert into bitland.claim(claimed_output_parcel_id, claim_action_output_parcel_id, claim_fee_sats, claim_block_height, invalidation_input_parcel_id, status, claim_end_block, from_bitland_block_height)
	select claimed_output_parcel_id, claim_action_output_parcel_id, claim_fee_sats, claim_block_height, invalidation_input_parcel_id, 'EXPIRED_CONFIRMED', claim_end_block, $3
	from bitland.claim c
	join expired e on c.id = e.id
	)
	update bitland.claim c
	set to_bitland_block_height = $3
	from expired e
	where e.id = c.id;

	return $1;

end;
$$;

drop function if exists bitland.update_invalidated_claims (bitland_block_height int);
create function bitland.update_invalidated_claims (bitland_block_height int)
returns int
language plpgsql
as
$$
declare

begin

	with moved_parcels as (
		select 
		  case 
		    when status = 'OPEN' then 'INVALIDATED'
		    when status = 'LEADING' and t.block_id < claim_end_block then 'INVALIDATED'
		    when status = 'LEADING' and t.block_id >= claim_end_block then 'ERROR - moved when should have been successful claim'
		  end as status
		  , c.id
		from bitland.claim c
		join bitland.output_parcel op on c.claimed_output_parcel_id = op.id
		  and c.status in ('OPEN','LEADING')
		join bitland.input_parcel ip on op.id = ip.output_parcel_id 
		join bitland.transaction t on ip.transaction_id = t.id
	)
	, insert_new_record as (
	insert into bitland.claim(claimed_output_parcel_id, claim_action_output_parcel_id, claim_fee_sats, claim_block_height, invalidation_input_parcel_id, status, claim_end_block, from_bitland_block_height)
	select claimed_output_parcel_id, claim_action_output_parcel_id, claim_fee_sats, claim_block_height, invalidation_input_parcel_id, e.status, claim_end_block, $1
	from bitland.claim c
	join moved_parcels e on c.id = e.id
	)
	update bitland.claim c
	set to_bitland_block_height = $1
	from moved_parcels e
	where e.id = c.id;

	return $1;

end;
$$;

drop function if exists bitland.update_leading_claims (bitland_block_height int, claim_blocks int, claim_increase float8);
create function bitland.update_leading_claims (bitland_block_height int, claim_blocks int, claim_increase float8)
returns int
language plpgsql
as
$$
declare

begin
	
	with fee_paid_claims as (
	select c.id, c.claim_fee_sats, claimed_output_parcel_id, c.claim_block_height, c.claim_action_output_parcel_id , c.invalidation_input_parcel_id, c.claim_end_block 
	from bitland.claim c
	join bitland.output_parcel op on c.claim_action_output_parcel_id = op.id
	  and c.status in ('OPEN') and c.to_bitland_block_height is null
	join bitland.vw_contingency_status vcs on op.transaction_id = vcs.id
	  and vcs.validation_recorded_bitland_block_height = $1 
	)
	--select * from fee_paid_claims
	--these three steps are needed to settle ties of multiple claims on same utxo
	, max_fee as (
	select claimed_output_parcel_id, max(claim_fee_sats) as max_claim_fee_sats
	from fee_paid_claims
	group by 1
	)
	, earliest_block_max_fee as (
	select fpc.claimed_output_parcel_id, fpc.claim_fee_sats, min(claim_block_height) as min_claim_block_height
	from max_fee mf
	join fee_paid_claims fpc on mf.claimed_output_parcel_id = fpc.claimed_output_parcel_id and mf.max_claim_fee_sats = fpc.claim_fee_sats
	group by 1,2
	)
	, winning_claims as (
	select fpc.*
	from fee_paid_claims fpc
	join earliest_block_max_fee ebmf on ebmf.claimed_output_parcel_id = fpc.claimed_output_parcel_id and ebmf.claim_fee_sats = fpc.claim_fee_sats and ebmf.min_claim_block_height = claim_block_height
	)
	--select * from winning_claims
	, valid_fee_increase as (
	select wc.id, wc.claimed_output_parcel_id, wc.claim_action_output_parcel_id, wc.claim_fee_sats, wc.claim_block_height, wc.invalidation_input_parcel_id, 'LEADING' as status, $1 + $2 as claim_end_block
	from winning_claims wc
	left join bitland.claim c on wc.claimed_output_parcel_id = c.claimed_output_parcel_id 
	  and c.status = 'LEADING' and c.to_bitland_block_height is null
	where (wc.claim_fee_sats::float8 / coalesce(c.claim_fee_sats,1)::float8) > $3
	)
	--select * from valid_fee_increase
	, superceded_claims as (
	select c.id, c.claimed_output_parcel_id, c.claim_action_output_parcel_id, c.claim_fee_sats, c.claim_block_height, c.invalidation_input_parcel_id, 'SUPERCEDED' as status, c.claim_end_block
	from valid_fee_increase v
	join bitland.claim c on v.claimed_output_parcel_id = c.claimed_output_parcel_id 
	  and c.status = 'LEADING' and c.to_bitland_block_height is null
	)
	--select * from superceded_claims
	, losing_or_invalid_claims as (
	select fpc.id, fpc.claimed_output_parcel_id, fpc.claim_action_output_parcel_id, fpc.claim_fee_sats, fpc.claim_block_height, fpc.invalidation_input_parcel_id, 'SUPERCEDED' as status, fpc.claim_end_block
	from fee_paid_claims fpc
	left join valid_fee_increase vfi on vfi.id = fpc.id
	where vfi.id is null
	)
	, all_updates as (
	select * from valid_fee_increase 
	union
	select * from superceded_claims
	union
	select * from losing_or_invalid_claims
	)
	, insert_new_record as (
	insert into bitland.claim(claimed_output_parcel_id, claim_action_output_parcel_id, claim_fee_sats, claim_block_height, invalidation_input_parcel_id, status, claim_end_block, from_bitland_block_height)
	select claimed_output_parcel_id, claim_action_output_parcel_id, claim_fee_sats, claim_block_height, invalidation_input_parcel_id, status, claim_end_block, $1
	from all_updates
	)
	update bitland.claim c
	set to_bitland_block_height = $1
	from all_updates a
	where a.id = c.id;

	return $1;

end;
$$;

drop function if exists bitland.update_successful_claims (bitland_block_height int, claim_blocks int);
create function bitland.update_successful_claims (bitland_block_height int, claim_blocks int)
returns int
language plpgsql
as
$$
declare

begin

	with successful_claims as (
	select c.id, 'SUCCESSFUL' as status
	from bitland.claim c
	where c.status = 'LEADING' 
	  and c.to_bitland_block_height is null 
	  and c.claim_end_block + $2 = $1
	)
	, insert_new_record as (
	insert into bitland.claim(claimed_output_parcel_id, claim_action_output_parcel_id, claim_fee_sats, claim_block_height, invalidation_input_parcel_id, status, claim_end_block, from_bitland_block_height)
	select claimed_output_parcel_id, claim_action_output_parcel_id, claim_fee_sats, claim_block_height, invalidation_input_parcel_id, e.status, claim_end_block, $1
	from bitland.claim c
	join successful_claims e on c.id = e.id
	)
	update bitland.claim c
	set to_bitland_block_height = $1
	from successful_claims e
	where e.id = c.id;	

	return $1;

end;
$$;

--
--OTHER
--

/* RESET SCRIPT
truncate bitland.block cascade;
truncate bitland.block_serialized cascade;
truncate bitland.transaction cascade;
truncate bitland.output_parcel cascade;
truncate bitland.claim cascade;
truncate bitland.transfer_fee_transaction;
truncate bitland.miner_fee_transaction;
truncate bitcoin.relevant_contingency_transaction;
truncate bitcoin.recent_transactions;
update landbase_enum set valid_claim = false;
update landbase_enum set block_claim = null;
update landbase_enum set valid_claim = true, valid_enabled_block = 0 where y_id in (1,975);
truncate bitland.transaction_mempool;
--	truncate wallet.addresses;

insert into bitland.block(id, header_hash) values
(0, '0000000000000000000000000000000000000000000000000000000000000000');

insert into bitland.block_serialized values 
(0,'00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000');

 */




