# Subscription system for authors (hw05_final).

Added Follow model, it has the following fields:
user - a link to the user object that is being subscribed.
author - a link to the user object that are being subscribed to
A view-function of the page has been created, where the posts of the authors, to which the current user is subscribed, are displayed.
Two more view-functions are created for subscribing to an interesting author and in order to unsubscribe from a boring graphomaniac

# Tests
Tests have been written to check the operation of the new service:
An authorized user can subscribe to other users and remove them from subscriptions.
A new user post appears in the feed of those who are subscribed to it and does not appear in the feed of those who are not subscribed to it.
Only an authorized user can comment on posts.

1.Using sorl-thumbnail, illustrations for posts are displayed:
to the master page template,
to the author profile template,
to the group page template.
2. Tests are written that check:
that when displaying a post with a picture, the image is passed in the context dictionary
to Home Page,
to the profile page,
to the group page,
to a separate page of the post;
that when you send a post with a picture through the PostForm form, a record is created in the database;
that if the page is not found then the server returns a 404 code.
3. A comment system has been created
A system for commenting records has been written. On the post page, under the post text, a form for submitting a comment is displayed, and below - a list of comments.
4. Caching the main page
The list of posts on the main page of the site is stored in the cache and is updated every 20 seconds.
5. Testing the cache
A test has been written to check the caching of the main page. Test logic: when an entry is deleted from the database, it remains in the response.content of the main page until the cache is cleared forcibly.
