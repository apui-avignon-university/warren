# Contributing to Warren TdbP

Thank you for considering contributing to Warren TdbP plugin! We appreciate your
interest and support. This documentation provides guidelines on how to contribute
effectively to our project.

## Issues

Issues are a valuable way to contribute to Warren TdbP. They can include bug reports,
feature requests, and general questions or discussions. When creating or
interacting with issues, please keep the following in mind:

### 1. Search for existing issues

Before creating a new issue, search the
[existing issues](https://github.com/apui-avignon-university/warren-tdbp/issues)
to see if your concern has already been raised. If you find a related issue, you
can add your input or follow the discussion. Feel free to engage in discussions,
offer help, or provide feedback on existing issues. Your input is valuable in
shaping the project's future.

### 2. Creating a new issue

When opening an issue, provide as much information as possible when writing
your issue. Your issue will be reviewed by a project maintainer and you may be
offered to open a PR if you want to contribute to the code. If not, and if your
issue is relevant, a contributor will apply the changes to the project. The
issue will then be automatically closed when the PR is merged.

Issues will be closed by project maintainers if they are deemed invalid. You can
always reopen an issue if you believe it hasn't been adequately addressed.

### 3. Code of conduct in discussion

- Be respectful and considerate when participating in discussions.
- Avoid using offensive language, and maintain a positive and collaborative
  tone.
- Stay on topic and avoid derailing discussions.

## Discussions

Discussions in the Warren TdbP repository are a place for open-ended conversations,
questions, and general community interactions. Here's how to effectively use
discussions:

### 1. Creating a discussion

- Use a clear and concise title that summarizes the topic.
- In the description, provide context and details regarding the discussion.
- Use labels to categorize the discussion (e.g., "question," "general
  discussion," "announcements," etc.).

### 2. Participating in discussions

- Engage in conversations respectfully, respecting others' opinions.
- Avoid spamming or making off-topic comments.
- Help answer questions when you can.

## Pull Requests (PR)

Contributing to Warren through pull requests is a powerful way to advance the
project. If you want to make changes or add new features, please follow these
steps to submit a PR:

### 1. Fork the repository

Begin by forking Warren TdbP project's repository.

### 2. Clone the fork

Clone the forked repository to your local machine and change the directory to
the project folder using the following commands (replace `<your_fork>` with your
GitHub username):

```bash
git clone https://github.com/<your_fork>/warren-tdbp.git
cd warren-tdbp
```

### 3. Create a new branch

Create a new branch for your changes, ideally with a descriptive name:

```bash
git checkout -b your-new-feature
```

### 4. Push changes

Push your branch to your GitHub repository:

```bash
git push origin feature/your-new-feature
```

### 5. Create a pull request

To initiate a Pull Request (PR), head to Warren TdbP project's GitHub repository
and click on <kbd>New Pull Request</kbd>.

Set your branch as the source and Warren TdbP project's `main` branch as the target.

Provide a clear title for your PR and make use of the provided PR body template
to document the changes made by your PR. This helps streamline the review
process and maintain a well-documented project history.

### 7. Review and discussion

Warren TdbP project maintainers will review your PR. Be prepared to make necessary
changes or address any feedback. Patience during this process is appreciated.

### 8. Merge

Once your PR is approved, Warren maintainers will merge your changes into the
main project. Congratulations, you've successfully contributed to Warren TdbP! 🎉

## Releases

The Warren TdbP project has multiple services maintained in a single Git repository
(_aka_ a monorepo): each service has its own life cycle with its own releases.

We use Git tags to trigger CI builds of the Warren TdbP's artifacts (PyPI/NPM
packages and Docker images). To make a new release, depending on the service you
are releasing, you need to apply the following Git tag pattern conventions:

| Type         | Service  | Git tag pattern              | Example       |
| ------------ | -------- | ---------------------------- | ------------- | 
| Back-end     | API      | `v[0-9]+.[0-9]+.[0-9]+-api`  | `v2.0.1-api`  |
|              | APP      | `v[0-9]+.[0-9]+.[0-9]+-app`  | `v1.3.6-app`  |
| Front-end    | tdbp     | `v[0-9]+.[0-9]+.[0-9]+-ui`   | `v5.1.0-ui`   |
| Distribution | \*       | `v[0-9]+.[0-9]+.[0-9]+`      | `v2.0.0`      |
| Helm         | \*       | `v[0-9]+.[0-9]+.[0-9]+-helm` | `v1.2.1-helm` |

!!! Note "About Warren TdbP distributions"

    A Warren **distribution** is considered as a "meta" package corresponding
    to a consistent combination of services releases that are known to work well
    together. This pattern will be used to tag Docker images and the documentation.

