

drop table if exists bitland.contingency ;
create table bitland.contingency (
  id serial, 
  output_parcel_id int, 
  miner_fee_status varchar, 
  transfer_fee_status varchar, 
  output_status varchar, 
  from_bitland_block_height int, 
  to_bitland_block_height int,
  CONSTRAINT contingency_output_parcel_id_fkey FOREIGN KEY (output_parcel_id) REFERENCES bitland.output_parcel(id)
);

alter table bitland.block add column bitcoin_hash varchar;
alter table bitland.block add column bitcoin_last_64_mrkl varchar;



RERUN VIEWS



--fake transactions
insert into bitcoin.recent_transactions values (695556, 'bc1q2vla02kvsslyfdg3tpdwt6whmfrsdkc7d0kkws', 11000, 'd6da80afac7d0a736784eb8cf38db8a2681f7a420ef41b83ff22cb3ffab5097c');
insert into bitcoin.recent_transactions values (695571, 'bc1q2vla02kvsslyfdg3tpdwt6whmfrsdkc7d0kkws', 17500, 'd6da80afac7d0a736784eb8cf38db8a2681f7a420ef41b83ff22cb3ffab5097c');
insert into bitcoin.recent_transactions values (696107, 'bc1qh2kwf0yfrlt3pqs97j5na82t8kdqzq74ycftgn',13052,'asdfas');
insert into bitcoin.recent_transactions values (696150, 'bc1q2vla02kvsslyfdg3tpdwt6whmfrsdkc7d0kkws',41010,'asdfas');




