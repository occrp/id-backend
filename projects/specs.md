# Editorial Pipeline

The goal is to have complete insight into the process of developing stories within OCCRP, from basic research through to initial writing, to editing, copy editing, and publication.

The intended product is a Django application that can exist standalone or plug in to our existing Investigative Dashboard (ID) project (thereby exposing more features). It should base off ID's user model and other infrastructure.

## Technology Stack
 * Django
 * Jinja2
 * Angular JS
 * JQuery
 * Bootstrap

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
 * A Journalist can write a story
 * An Editor can write and alter a story
 * A Copy Editor can alter a story
 * A Researcher can add Documents to a story
 * An Artist can add art to a story 
 * A Translator can create a Translation of a story
 * An Editor can see a story overview, showing all Stories currently in the pipeline, along with what their status is
 * A Journalist, Researcher, Copy Editor, Artist, and Translator can all see the stories they are working on
 * An Editor can prioritize the stories that a Copy Editor or Translator are working on
 * A Journalist, Researcher, Editor, Copy Editor or Translator can post questions or comments on a story that others assigned to the story are notified about and can view.
 * An Editor can lock a story against changes 
 * A user can compare previous versions of the story

## Cross-functional Requirements
 * Application interactions provided through Angular JS
 * Jinja2 as templating engine as needed, not Django's default templating engine
 * Fully unit tested (using Django's unit test framework)
 * Fully integration tested
 * All core logic in models or separate classes, not in views or templates
 * No unit composition in units