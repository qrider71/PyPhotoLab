-- Main table for storing attributes of photos
create table photos
(
    id         integer primary key,
    file_size  integer not null,
    timestamp  integer,
    date_time  text,
    lat_deg    real,
    lon_deg    real,
    hash_value text    not null
);

create unique index photos_hash_idx on photos (hash_value);

-- Table with paths for photos, a photo can exist multiple times with different paths
create table paths
(
    id       integer primary key,
    photo_id integer not null,
    path     text    not null,
    foreign key (photo_id) references photos (id) on delete cascade
);

create unique index paths_path_idx on paths (path);
create unique index paths_path_photoid_idx on paths (path, photo_id);

-- holds output of the geographic clustering, each coordinate is assigned to a cluster label
create table clusters
(
    id       integer primary key,
    label    integer not null,
    lat_deg  real    not null,
    lon_deg  real    not null,
    hull_idx integer
);

create unique index clusters_coords_idx on clusters (lat_deg, lon_deg);

-- view for accessing all coordinates
create view all_coords_view
as
select photos.lat_deg,
       photos.lon_deg
from photos
where photos.lat_deg is not null
  and photos.lon_deg is not null;


-- view for associating photos (referred by their id) with cluster labels
create view all_photos_clustered_view
as
select p.id, p.lat_deg, p.lon_deg, c.label
from photos p
         inner join clusters c on p.lat_deg = c.lat_deg and p.lon_deg = c.lon_deg;


-- calculates center coordinates for each cluster (weighted average by number of photos,
-- i.e. coordinates with more photos have higher weight)
create view cluster_centers_view as
select p.label, avg(p.lat_deg) as lat_deg, avg(p.lon_deg) as lon_deg, count(*) as count_photos
from all_photos_clustered_view p
group by p.label
order by p.label;

create view cluster_hull_view as
select c.label, c.lat_deg, c.lon_deg, c.hull_idx
from clusters c
where c.hull_idx is not null
order by c.label, c.hull_idx;

create view duplicate_photos_ids_view as
select pa.photo_id, count(*) num
from paths pa
group by pa.photo_id
having num > 1;

create view duplicate_photos_id_paths_view as
select pa.photo_id, pa.path, pam.num
from duplicate_photos_ids_view pam
         inner join paths pa on pam.photo_id = pa.photo_id
order by pa.photo_id, pa.path;