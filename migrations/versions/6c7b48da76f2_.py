"""empty message

Revision ID: 6c7b48da76f2
Revises: 6d289396041a
Create Date: 2020-12-30 23:07:56.555178

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6c7b48da76f2'
down_revision = '6d289396041a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('question',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('question_title', sa.String(), nullable=True),
    sa.Column('question_body', sa.Text(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('course_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['course_id'], ['course.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_question_timestamp'), 'question', ['timestamp'], unique=False)
    op.drop_table('friends')
    op.drop_table('friend_requests')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('friend_requests',
    sa.Column('requester_id', sa.INTEGER(), nullable=True),
    sa.Column('requested_id', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['requested_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['requester_id'], ['user.id'], )
    )
    op.create_table('friends',
    sa.Column('friend_id', sa.INTEGER(), nullable=True),
    sa.Column('befriended_id', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['befriended_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['friend_id'], ['user.id'], )
    )
    op.drop_index(op.f('ix_question_timestamp'), table_name='question')
    op.drop_table('question')
    # ### end Alembic commands ###