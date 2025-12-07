from django.db import migrations


def seed_rbac_v2(apps, schema_editor):
    User = apps.get_model('users', 'User')
    Role = apps.get_model('users', 'Role')
    Permission = apps.get_model('users', 'Permission')
    RolePermission = apps.get_model('users', 'RolePermission')
    UserRole = apps.get_model('users', 'UserRole')

    roles_data = [
        ('admin', 'admin'),
        ('manager', 'manager'),
        ('user', 'user')
    ]

    roles = {}
    for code, _ in roles_data:
        role, created = Role.objects.update_or_create(
            name=code,
            defaults={
                'source': 'migration_0006_v2'
            }
        )
        roles[code] = role

    permission_data = [
        'users.view', 'users.edit', 'users.delete', 'users.list',
        'objects.view', 'objects.edit', 'objects.delete',
        'self.view', 'self.edit', 'self.delete'
    ]

    permissions = {}
    for code in permission_data:
        permission, created = Permission.objects.update_or_create(
            code=code,
            defaults={
                'source': 'migration_0006_v2'
            }
        )
        permissions[code] = permission

    role_permission_mapping = {
        'admin': [
            'users.view', 'users.edit', 'users.delete',
            'users.list', 'objects.view', 'objects.edit',
            'objects.delete', 'self.view', 'self.edit',
            'self.delete'
        ],
        'manager': [
            'users.view', 'users.list', 'objects.view',
            'self.view', 'self.edit', 'self.delete'
        ],
        'user': [
            'objects.view', 'self.view', 'self.edit',
            'self.delete'
        ]
    }

    for role_code, perm_codes in role_permission_mapping.items():
        role = roles[role_code]

        RolePermission.objects.filter(role=role).delete()

        for perm_code in perm_codes:
            permission = permissions[perm_code]
            RolePermission.objects.create(role=role, permission=permission)

    user_roles_mapping = [
        ('geney@gmail.com', 'admin'),
        ('test@mail.com', 'manager')
    ]

    for email, role_code in user_roles_mapping:
        try:
            user = User.objects.get(email=email)
            role = roles[role_code]
            UserRole.objects.filter(user=user).delete()
            UserRole.objects.create(user=user, role=role)
        except User.DoesNotExist:
            print(f"User {email} not found, skipping role assignment")

    print(f"Created/updated {len(roles)} roles and {len(permissions)} permissions")


def reverse_seed_v2(apps, schema_editor):
    Role = apps.get_model('users', 'Role')
    Permission = apps.get_model('users', 'Permission')

    Role.objects.filter(source='migration_0006_v2').delete()
    Permission.objects.filter(source='migration_0006_v2').delete()


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0005_add_source_field'),
    ]

    operations = [
        migrations.RunPython(seed_rbac_v2, reverse_seed_v2),
    ]
