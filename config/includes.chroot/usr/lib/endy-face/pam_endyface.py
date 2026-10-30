"""PAM glue (pam_python). Placed as `auth sufficient` before the password stack in /etc/pam.d/lightdm.

Returns SUCCESS only on a confirmed face match. Every other outcome (no template, no camera, any error,
no match) falls through to the normal password prompt, so a bug here can never lock the user out.
"""
import sys
import syslog

sys.path.insert(0, "/usr/lib/endy-face")


def pam_sm_authenticate(pamh, flags, argv):
    try:
        import face
        user = pamh.get_user(None)
        if not user or not face.is_enrolled(user):
            return pamh.PAM_IGNORE
        source = 0
        for a in argv[1:]:                      # argv[0] is this file; options come from root-owned PAM config
            if a.startswith("source="):
                source = a[len("source="):]
        ok = face.verify(user, source)
        syslog.syslog(syslog.LOG_INFO, "endy-face: %s for %s" % ("match" if ok else "no match", user))
        return pamh.PAM_SUCCESS if ok else pamh.PAM_AUTH_ERR
    except Exception as exc:                    # never block password login
        syslog.syslog(syslog.LOG_WARNING, "endy-face: ignored (%s)" % exc)
        return pamh.PAM_IGNORE


def pam_sm_setcred(pamh, flags, argv):
    return pamh.PAM_SUCCESS


def pam_sm_acct_mgmt(pamh, flags, argv):
    return pamh.PAM_SUCCESS
