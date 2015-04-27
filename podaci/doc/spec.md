
Generic:
	get_json()				Get JSON blob
	get_details_string()	Get details string
	log()					Add log entry

Permissions:
	Give user read permissions
	Give user write permissions
	Revoke user read permissions
	Revoke user write permissions
	Give public read permissions
	Give staff read/write permissions
	Check if user has read permissions
	Check if user has write permissions

File:
	load()						Alias for load_by_id()
	load_by_id()				Load from ID
	load_by_hash()				Load from hash
	exists_by_hash()			Check if file with hash exists
	exists_by_id()				Check if file with ID exists
	create_from_filehandle()	Create from file handle
	Get file metadata
	Get file contents
	Set file metadata
	List tags
	Add a tag
	Add a note
	Delete a note
	List notes
	Get Thumbnail
	Delete

Tag:
	Load from ID
	Create by name
	List files in tag
	List children tags
	List parent tags
	Get tag metadata
	Set tag metadata
	Create a child tag
	Set a tag as parent
	Check if tag is empty
	Get contents as a Zip file
	Delete
