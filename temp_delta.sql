
create schema bitcoin;

drop table if exists bitcoin.recent_transactions;
create table bitcoin.recent_transactions(bitcoin_block_height int, address varchar, value float8, txid varchar);

drop table if exists bitcoin.relevant_contingency_transaction;
create table bitcoin.relevant_contingency_transaction (bitcoin_block_height int, address varchar, value float8, txid varchar, recorded_bitland_block_height int);

drop table if exists bitcoin.block;
create table bitcoin.block(block_height int, block_hash varchar);

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

drop view if exists bitcoin.transaction_blocks;
create view bitcoin.transaction_blocks as (
  select distinct bitcoin_block_height
  from bitcoin.recent_transactions
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
	select c.id, c.claim_fee_sats, claimed_output_parcel_id, c.claim_block_height
	from bitland.claim c
	join bitland.output_parcel op on c.claim_action_output_parcel_id = op.id
	  and c.status in ('OPEN') and c.to_bitland_block_height is null
	join bitland.vw_contingency_status vcs on op.transaction_id = vcs.id
	  and vcs.validation_recorded_bitland_block_height = $1 
	)
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
	, valid_fee_increase as (
	select wc.id, c.claimed_output_parcel_id, c.claim_action_output_parcel_id, c.claim_fee_sats, c.claim_block_height, c.invalidation_input_parcel_id, 'LEADING' as status, $1 + $2 as claim_end_block
	from winning_claims wc
	left join bitland.claim c on wc.claimed_output_parcel_id = c.claimed_output_parcel_id 
	  and c.status = 'LEADING' and c.to_bitland_block_height is null
	where (wc.claim_fee_sats / coalesce(c.claim_fee_sats,1) - 1) > $3
	)
	, superceded_claims as (
	select c.id, c.claimed_output_parcel_id, c.claim_action_output_parcel_id, c.claim_fee_sats, c.claim_block_height, c.invalidation_input_parcel_id, 'SUPERCEDED' as status, c.claim_end_block
	from valid_fee_increase v
	join bitland.claim c on v.claimed_output_parcel_id = c.claimed_output_parcel_id 
	  and c.status = 'LEADING' and c.to_bitland_block_height is null
	)
	, losing_or_invalid_claims as (
	select vfi.id, vfi.claimed_output_parcel_id, vfi.claim_action_output_parcel_id, vfi.claim_fee_sats, vfi.claim_block_height, vfi.invalidation_input_parcel_id, 'SUPERCEDED' as status, vfi.claim_end_block
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




alter table bitland.claim add column status varchar;
alter table bitland.claim add column claim_end_block int;
alter table bitland.claim drop column leading_claim;
alter table bitland.claim drop column invalidated_claim;