# Editorial Pipeline

The goal is to have complete insight into the process of developing stories within OCCRP, from basic research through to initial writing, to editing, copy editing, and publication.

The intended product is a Django application that can exist standalone or plug in to our existing Investigative Dashboard (ID) project (thereby exposing more features). It should base off ID's user model and other infrastructure.

## Technology Stack
 * Django
 * Django REST Framework
 * Jinja2
 * Web components
 * Polymer
 * Paper

## User Roles
 * Staff [Exists as is_staff in User Profile]
 * Researcher
 * Journalist 
 * Editor 
 * Copy editor
 * Translator
 * Artist

## Core concepts
 * Story
 * Language
 * Translation
 * Documents (images, PDF files, etc)
 * Artwork (photos, graphics, art) 

## General requirements
 * An Editor can be assigned to 0 or more Stories
 * A Journalist can be assigned to 0 or more Stories
 * A Researcher can be assigned to 0 or more Stories
 * A Copy Editor can be assigned to 0 or more Stories
 * A Translator can be assigned to 0 or more Stories
 * A Translator can be assigned to 0 or more Languages
 * An Artist can be assigned to 0 or more Stories 
 * A Story can have 0 or more of any of the above
 * A Story can have different statuses. Statuses pre-defined but editable (add new statuses; mark as unused from now on)
 * Each Story has an associated Podaci root tag (ask Smári what that means), through which all associated file management occurs. Any subtags or files are viewable as part of the story.

## User Stories
 * Only logged in users with Staff permissions can use the system
 * A Journalist or an Editor can start a new story
 * If a Journalist starts a new story, they are automatically assigned to it.
 * Editors are notified when there are stories that have no editor
 * An Editor can assign Journalists, Researchers, Copy Editors, Translators, and other Editors to a Story
 * A User with access to a story can write a new version of a story
 * A User with access to a story can upload a Word document, which gets stored as a new version of a story
 * A User with access to a story can upload a Markdown document, which gets stored as a new version of a story
 * A User with access to a story can compare different versions of a story
 * An Editor can write and alter a story
 * A Copy Editor can alter a story
 * A Researcher can add Documents to a story
 * An Artist can add art to a story 
 * A Translator can create a Translation of a story
 * An Editor can see a story overview, showing all Stories currently in the pipeline, along with what their status is
 * A Journalist, Researcher, Copy Editor, Artist, and Translator can all see the stories they are working on
 * An Editor can prioritize the stories that a Copy Editor or Translator are working on
 * A Journalist, Researcher, Editor, Copy Editor or Translator can post questions or comments on a story or versions of stories that others assigned to the story are notified about and can view.
 * An Editor can lock a story against changes 
 * A User who's assigned to a Project can post comments on the project 

## Cross-functional Requirements
 * Application interactions provided through Web Components
 * Jinja2 as templating engine as needed, not Django's default templating engine
 * Fully unit tested (using Django's unit test framework)
 * Fully integration tested
 * All core logic in models or separate classes, not in views or templates
 * No unit composition in units
 * 

## REST Endpoints

### Project (collection)
 * POST /api/projects/                - Create new project (params: title)
 * GET /api/projects/                 - Get list of projects

### Project (member)
 * GET /api/projects/<pid>/            - Get project <pid>
 * DELETE /api/projects/<pid>/         - Delete project <pid>
 * PUT /api/projects/<pid>/            - Alter the project configuration
 * POST /api/projects/<pid>/           - Update the status of the project

### Project Users (collection)
 * POST /api/projects/<pid>/users/     - Add user to project <pid> (params: userid)
 * DELETE /api/projects/<pid>/users/   - Remove user from project <pid> (params: userid)
 * GET /api/projects/<pid>/users/      - List users on project

### Project Stories (collection)
 * POST /api/projects/<pid>/stories/   - Add a new story to project
 * GET /api/projects/<pid>/stories/    - List stories on the project

### Project Stories (member)
 * GET /api/stories/<sid>/             - Get the details of a story
 * DELETE /api/stories/<sid>/          - Delete a story
 * GET /api/stories/<sid>/<vid>/       - Get a version of a story
 * DELETE /api/stories/<sid>/<vid>/    - Delete a version of a story
 * PUT /api/stories/<sid>/             - Update story settings
 * POST /api/stories/<sid>/            - Add new version of a story
 * POST /api/stories/<sid>/files/      - Add a file to a story
 * POST /api/stories/<sid>/art/        - Add a file to a story
 * GET /api/stories/<sid>/live/        - Get the most recent version of a story 
                                         in the specified language if 
                                         available, or 404.

### Story Translations (collection/member)

 * GET /api/translations/<vid>/<lang>/ - Get the translation of the story for a 
                                         given version, or 404, or 403
 * POST /api/translations/<vid>/       - Add a translation for a given version 
                                         of the story.
 * PUT /api/translations/<vid>/        - Update a translation for a given 
                                         version of the story
 * DELETE /api/translations/<vid>/     - Delete a translation for a given 
                                         version of a story

### Project Plans (collection)
 * POST /api/projects/<pid>/plans/     - Add a new plan to the project
 * GET /api/projects/<pid>/plans/      - List plans for the project

### Project Plans (member)
 * GET /api/plans/<plid>/              - Get the details of a plan
 * PUT /api/plans/<plid>/              - Update a plan
 * DELETE /api/plans/<plid>/           - Delete a plan

## REST Endpoint Guidelines
* A User can only see a Project they are coordinator of or are a member of
* A User can see all stories in a Project they are a member of
* A User can only alter a story if they are assigned to it
