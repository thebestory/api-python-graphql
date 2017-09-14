"""
The Bestory Project
"""

import logging

import graphene

from tbs import models
from tbs.graphql.queries.story import Story
from tbs.lib import exceptions
from tbs.lib import session
from tbs.lib.graphql import scalars


# class SubmitStoryAuthorInput(graphene.InputObjectType):
#     id = scalars.Snowflake(default_value=0)
#     username = graphene.String(default_value="None")


# class SubmitStoryTopicInput(graphene.InputObjectType):
#     id = scalars.Snowflake(default_value=0)
#     slug = graphene.String(default_value="unsorted")  # Constant!


class SubmitStoryInput(graphene.InputObjectType):
    # author = graphene.InputField(SubmitStoryAuthorInput)
    # topic = graphene.InputField(SubmitStoryTopicInput)
    author_id = scalars.Snowflake(default_value=0)
    author_username = graphene.String(default_value="")
    topic_id = scalars.Snowflake(default_value=0)
    topic_slug = graphene.String(default_value="unsorted")
    content = graphene.String(required=True)
    is_published = graphene.Boolean(default_value=False)


class SubmitStoryPayload(graphene.Mutation):
    class Arguments:
        input = graphene.Argument(SubmitStoryInput, required=True)

    story = graphene.Field(Story)

    @staticmethod
    @session.login_required
    async def mutate(root, info, input):
        submitter = info.context["request"]["session"]["viewer"]

        try:
            if input.author_id is not None and input.author_id != 0:
                author = await models.User.get(id=input.author_id)
            elif input.author_username is not None and input.author_username != "":
                author = await models.User.get_by_username(
                    input.author_username)
            else:
                author = submitter
        except exceptions.NotFoundError:
                raise exceptions.TheBestoryError("Author is not found")

        try:
            if input.topic_id is not None and input.topic_id != 0:
                topic = await models.Topic.get(id=input.topic_id)
            elif input.topic_slug is not None and input.topic_slug != "":
                topic = await models.Topic.get_by_slug(input.topic_slug)
            else:
                raise exceptions.TheBestoryError("Topic must be specified")
        except exceptions.NotFoundError:
                raise exceptions.TheBestoryError("Topic is not found")

        story = models.Story(author_id=author.id, 
                             topic_id=topic.id,
                             content=input.content,
                             is_published=input.is_published)

        try:
            await story.save()
        except exceptions.NotSavedError:
            raise exceptions.TheBestoryError("Error during story submition")

        return SubmitStoryPayload(story=Story(from_model=story))
