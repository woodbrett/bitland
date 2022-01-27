
ALTER TABLE bitland.block ADD CONSTRAINT block_header_hash_unique UNIQUE (header_hash);
ALTER TABLE bitland.block_serialized ADD CONSTRAINT block_serialized_unique UNIQUE (block);

alter table networking.peer add constraint ip_port_unique unique (ip_address, port);