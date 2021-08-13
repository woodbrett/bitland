
create schema bitcoin;

drop table if exists bitcoin.recent_transactions;
create table bitcoin.recent_transactions(bitcoin_block_height int, address varchar, value float8, txid varchar);

drop table if exists bitcoin.relevant_contingency_transaction;
create table bitcoin.relevant_contingency_transaction (bitcoin_block_height int, address varchar, value float8, txid varchar, recorded_bitland_block_height int);

drop table if exists bitcoin.block;
create table bitcoin.block(block_height int, block_hash varchar);

alter table bitland.claim add column status varchar;
alter table bitland.claim add column claim_end_block int;
alter table bitland.claim drop column leading_claim;
alter table bitland.claim drop column invalidated_claim;



RERUN VIEWS



--fake transactions
insert into bitcoin.recent_transactions values (695556, 'bc1q2vla02kvsslyfdg3tpdwt6whmfrsdkc7d0kkws', 11000, 'd6da80afac7d0a736784eb8cf38db8a2681f7a420ef41b83ff22cb3ffab5097c');
insert into bitcoin.recent_transactions values (695571, 'bc1q2vla02kvsslyfdg3tpdwt6whmfrsdkc7d0kkws', 17500, 'd6da80afac7d0a736784eb8cf38db8a2681f7a420ef41b83ff22cb3ffab5097c');





