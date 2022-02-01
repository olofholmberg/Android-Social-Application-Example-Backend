"""followers, friends

Revision ID: 6d289396041a
Revises: c45a565306ab
Create Date: 2020-12-21 13:07:52.770096

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6d289396041a'
down_revision = 'c45a565306ab'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('course',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('course_code', sa.String(), nullable=True),
    sa.Column('course_name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_course_course_code'), 'course', ['course_code'], unique=True)
    op.create_table('followers',
    sa.Column('follower_id', sa.Integer(), nullable=True),
    sa.Column('followed_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['followed_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['follower_id'], ['user.id'], )
    )
    op.create_table('friend_requests',
    sa.Column('requester_id', sa.Integer(), nullable=True),
    sa.Column('requested_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['requested_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['requester_id'], ['user.id'], )
    )
    op.create_table('friends',
    sa.Column('friend_id', sa.Integer(), nullable=True),
    sa.Column('befriended_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['befriended_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['friend_id'], ['user.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('friends')
    op.drop_table('friend_requests')
    op.drop_table('followers')
    op.drop_index(op.f('ix_course_course_code'), table_name='course')
    op.drop_table('course')
    # ### end Alembic commands ###
