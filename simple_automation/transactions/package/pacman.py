from simple_automation import Context
from simple_automation.transactions.basic import _template_str

def is_installed(context: Context, atom: str, packages=None):
    remote_query = context.remote_exec(["pacman", "-Ql", atom])
    return remote_query.return_code == 0

def package(context: Context, atom: str, state="present", opts=[]):
    """
    Installs or uninstalls (depending if state == "present" or "absent") the given
    package atom. Additional options to pacman can be passed via opts, and will be appended
    before the package atom. opts will be templated.
    """
    if state not in ["present", "absent"]:
        raise LogicError(f"Invalid package state '{state}'")

    atom = _template_str(context, atom)
    opts = [_template_str(context, o) for o in opts]

    with context.transaction(title="package", name=atom) as action:
        # Query current state
        installed = is_installed(context, atom)

        # Record this initial state, and return early
        # if there is nothing to do
        action.initial_state(installed=installed)
        should_install = (state == "present")
        if installed == should_install:
            return action.unchanged()

        # Record the final state
        action.final_state(installed=should_install)

        # Apply actions to reach new state, if we aren't in pretend mode
        if not context.pretend:
            if should_install:
                pacman_cmd = ["pacman", "--color", "always"]
                pacman_cmd.extend(opts)
                pacman_cmd.append(atom)

                context.remote_exec(pacman_cmd, checked=True, error_verbosity=0, verbosity=1)
            else:
                context.remote_exec(["pacman", "--color", "always", "-Rs"] + opts + [atom], checked=True, error_verbosity=0, verbosity=1)

        # Return success
        return action.success()
