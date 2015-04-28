from rest_framework import serializers

from .models import TrainingSurvey, TrainingSession, TrainingSubject

from dashboard.serializers import HouseholdSurveyJSONSerializer, HouseholdMemberSerializer, TeamMemberSerializer


class TrainingSubjectSerializer(HouseholdMemberSerializer):

    class Meta:
        model = TrainingSubject
        fields = HouseholdMemberSerializer.Meta.fields


class TrainingSurveySerializer(HouseholdSurveyJSONSerializer):

    members = TrainingSubjectSerializer(many=True, read_only=False)

    def create(self, validated_data):

        family_members = validated_data.pop('members')
        instance = super(TrainingSurveySerializer, self).create(validated_data)
        validated_data['members'] = family_members
        self.update(instance, validated_data)

        return instance

    def update(self, instance, validated_data):

        family_members = validated_data.pop('members')
        super(TrainingSurveySerializer, self).update(instance, validated_data)
        instance.members.all().delete()
        new_family = [TrainingSubject(index=index, household_survey=instance, **family_member)
                      for index, family_member in enumerate(family_members)]

        TrainingSubject.objects.bulk_create(new_family)

        return instance

    class Meta:
        model = TrainingSurvey
        extra_kwargs = HouseholdSurveyJSONSerializer.Meta.extra_kwargs

        fields = (
            'url',
            'uuid',
            'household_number',
            'members',
            'team_assistant',
            'team_anthropometrist',
            'first_admin_level',
            'second_admin_level',
            'cluster',
            'cluster_name',
            'start_time',
            'end_time',
            'members',
        )


class TrainingSurveySerializerWithMemberDetails(TrainingSurveySerializer):
    team_assistant = TeamMemberSerializer()
    team_anthropometrist = TeamMemberSerializer()


class TrainingSessionSerializer(serializers.ModelSerializer):

    # TODO make this a serializers.HyperlinkedModelSerializer
    # once users have URL

    class Meta:

        model = TrainingSession

        fields = [
            'id',
            'url',
            'created',
            'creator',
        ]
