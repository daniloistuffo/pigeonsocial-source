import os
import re
import html
from datetime import datetime, timedelta
from flask import Blueprint, flash, redirect, render_template, request, session, url_for, jsonify
from markupsafe import Markup
from werkzeug.security import check_password_hash, generate_password_hash
from database import get_db_connection

main_bp = Blueprint('main', __name__)

TRANSLATIONS = {
    'en': {
        'feed': 'Feed',
        'profile': 'Profile',
        'settings': 'Settings',
        'logout': 'Logout',
        'login': 'Login',
        'register': 'Register',
        'thinking': "What's on your mind today? Use #hashtags",
        'pigeon_mail': 'Send as Pigeon Mail',
        'publish': 'Publish',
        'login_prompt': 'Please login to post and interact.',
        'recent_posts': 'Recent Posts',
        'likes': 'Likes',
        'comments': 'Comments',
        'comment_placeholder': 'Write a comment...',
        'send': 'Send',
        'no_posts': 'No posts here yet. Be the first!',
        'banned_title': 'Account Banned',
        'banned_perm': 'Your account has been permanently banned.',
        'banned_temp': 'Your account is temporarily banned until:',
        'appeal_label': 'Submit an appeal to administrators:',
        'appeal_btn': 'Send Appeal',
        'username': 'Username',
        'password': 'Password',
        'birth_date': 'Birth Date',
        'age_error': 'You must be at least 13 years old to register.',
        'already_have_account': 'Already have an account?',
        'no_account': "Don't have an account?",
        'search_placeholder': 'Search #tag...',
        'search': 'Search',
        'direct_message': 'Direct Message',
        'update_bio': 'Update Bio',
        'bio_placeholder': 'Write about yourself...',
        'save_bio': 'Save Bio',
        'send_private_message': 'Send Private Message',
        'posts': 'Posts',
        'no_bio': 'No bio provided.',
        'chat_with': 'Chat with',
        'chat_placeholder': 'Type your message...',
        'back_to_feed': 'Back to Feed',
        'filtering_tag': 'Filtering by tag:',
        'clear_filter': 'Clear filter',
        'no_comments': 'No comments yet.',
        'mode': 'Mode',
        'follow': 'Follow',
        'unfollow': 'Unfollow',
        'followers': 'Followers',
        'following': 'Following',
        'select_avatar': 'Select Profile Avatar',
        'save_avatar': 'Save Avatar',
        'save_preferences': 'Save Preferences',
        'language': 'Language',
        'streak': 'Streak',
        'account_privacy': 'Account Privacy',
        'private_account': 'Private Account (Hide posts from non-followers)',
        'saved_posts': 'Saved Posts',
        'save_post': 'Save'
    },
    'pt': {
        'feed': 'Feed',
        'profile': 'Perfil',
        'settings': 'Definições',
        'logout': 'Sair',
        'login': 'Entrar',
        'register': 'Registar',
        'thinking': 'O que está a pensar hoje? Use #hashtags',
        'pigeon_mail': 'Enviar como Correio de Pombo',
        'publish': 'Publicar',
        'login_prompt': 'Faça login para publicar e interagir na rede.',
        'recent_posts': 'Publicações Recentes',
        'likes': 'Gostos',
        'comments': 'Comentários',
        'comment_placeholder': 'Escreva um comentário...',
        'send': 'Enviar',
        'no_posts': 'Nenhuma publicação por aqui ainda. Seja o primeiro!',
        'banned_title': 'Conta Banida',
        'banned_perm': 'A sua conta foi banida permanentemente.',
        'banned_temp': 'A sua conta está banida temporariamente até:',
        'appeal_label': 'Enviar apelo aos administradores:',
        'appeal_btn': 'Enviar Apelo',
        'username': 'Utilizador',
        'password': 'Palavra-passe',
        'birth_date': 'Data de Nascimento',
        'age_error': 'Deve ter pelo menos 13 anos para se registar.',
        'already_have_account': 'Já tem uma conta?',
        'no_account': 'Não tem uma conta?',
        'search_placeholder': 'Pesquisar #tag...',
        'search': 'Pesquisar',
        'direct_message': 'Mensagem Direta',
        'update_bio': 'Atualizar Biografia',
        'bio_placeholder': 'Escreva sobre si...',
        'save_bio': 'Guardar Bio',
        'send_private_message': 'Enviar Mensagem Privada',
        'posts': 'Publicações',
        'no_bio': 'Sem biografia.',
        'chat_with': 'Conversa com',
        'chat_placeholder': 'Escreva a sua mensagem...',
        'back_to_feed': 'Voltar ao Feed',
        'filtering_tag': 'Filtrando pela tag:',
        'clear_filter': 'Limpar filtro',
        'no_comments': 'Sem comentários.',
        'mode': 'Modo',
        'follow': 'Seguir',
        'unfollow': 'Deixar de Seguir',
        'followers': 'Seguidores',
        'following': 'A seguir',
        'select_avatar': 'Selecionar Avatar de Perfil',
        'save_avatar': 'Guardar Avatar',
        'save_preferences': 'Guardar Preferências',
        'language': 'Idioma',
        'streak': 'Ofensiva',
        'account_privacy': 'Privacidade da Conta',
        'private_account': 'Conta Privada (Ocultar publicações de não-seguidores)',
        'saved_posts': 'Publicações Guardadas',
        'save_post': 'Guardar'
    }
}

@main_bp.before_request
def check_bans_and_lang():
    if request.endpoint == 'main.logout':
        return

    if 'user_id' in session:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT is_perm_banned, banned_until, perm_banned_date, lang, theme FROM users WHERE id = ?', (session['user_id'],))
        user = cursor.fetchone()

        if user:
            session['lang'] = user['lang'] or 'en'
            session['theme'] = 'light'

            now = datetime.now()
            if user['is_perm_banned'] == 1:
                if request.endpoint not in ['main.banned', 'main.logout', 'main.submit_appeal']:
                    conn.close()
                    return redirect(url_for('main.banned'))
            elif user['banned_until']:
                b_until = datetime.strptime(user['banned_until'], '%Y-%m-%d %H:%M:%S')
                if now < b_until:
                    if request.endpoint not in ['main.banned', 'main.logout', 'main.submit_appeal']:
                        conn.close()
                        return redirect(url_for('main.banned'))
        conn.close()

    if 'lang' not in session:
        session['lang'] = 'en'
    session['theme'] = 'light'

@main_bp.app_template_global()
def t(key):
    lang = session.get('lang', 'en')
    return TRANSLATIONS.get(lang, TRANSLATIONS['en']).get(key, key)

@main_bp.app_template_filter('format_hashtags')
def format_hashtags(text):
    safe_text = html.escape(text)
    def replace_tag(match):
        tag = match.group(1)
        link = url_for('main.feed', tag=tag)
        return f'<a href="{link}" style="color: var(--primary); font-weight: bold; text-decoration: none;">#{tag}</a>'
    formatted = re.sub(r'#([a-zA-Z0-9_]+)', replace_tag, safe_text)
    return Markup(formatted)

@main_bp.route('/')
def index():
    return redirect(url_for('main.feed'))

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        birth_date_str = request.form.get('birth_date', '')

        if not re.match(r'^[a-zA-Z0-9.]+$', username):
            flash('Username can only contain letters, numbers and dots (.) without spaces.' if session['lang']=='en' else 'O nome de utilizador só pode conter letras, números e pontos (.) sem espaços.')
            return redirect(url_for('main.register'))

        if len(password) < 8:
            flash('Password must be at least 8 characters long.' if session['lang']=='en' else 'A palavra-passe deve ter pelo menos 8 carateres.')
            return redirect(url_for('main.register'))

        try:
            b_date = datetime.strptime(birth_date_str, '%Y-%m-%d')
            today = datetime.now()
            age = today.year - b_date.year - ((today.month, today.day) < (b_date.month, b_date.day))
            if age < 13:
                flash(TRANSLATIONS[session['lang']]['age_error'])
                return redirect(url_for('main.register'))
        except Exception:
            flash('Invalid birth date.' if session['lang']=='en' else 'Data de nascimento inválida.')
            return redirect(url_for('main.register'))

        hashed_password = generate_password_hash(password)
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('INSERT INTO users (username, password, birth_date, avatar, theme) VALUES (?, ?, ?, ?, ?)',
                           (username, hashed_password, birth_date_str, 'ProfileImage#1.png', 'light'))
            conn.commit()
            conn.close()
            flash('Account created successfully! Please login.' if session['lang']=='en' else 'Conta criada com sucesso! Faça login.')
            return redirect(url_for('main.login'))
        except Exception:
            flash('Username already in use.' if session['lang']=='en' else 'Este nome de utilizador já está em uso.')
            return redirect(url_for('main.register'))
    return render_template('register.html')

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, password, avatar, lang, theme FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()
        if user and user['password'] and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['avatar'] = user['avatar']
            session['lang'] = user['lang'] or 'en'
            session['theme'] = 'light'
            session.permanent = True
            flash('Welcome back!' if session['lang']=='en' else 'Bem-vindo de volta!')
            return redirect(url_for('main.feed'))
        else:
            flash('Incorrect username or password.' if session['lang']=='en' else 'Utilizador ou palavra-passe incorretos.')
            return redirect(url_for('main.login'))
    return render_template('login.html')

@main_bp.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.')
    return redirect(url_for('main.feed'))

@main_bp.route('/settings', methods=['GET', 'POST'])
def settings():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        new_lang = request.form.get('lang', 'en')
        new_theme = 'light'
        is_private = 1 if request.form.get('is_private') else 0

        session['lang'] = new_lang
        session['theme'] = 'light'

        cursor.execute('UPDATE users SET lang = ?, theme = ?, is_private = ? WHERE id = ?', (new_lang, new_theme, is_private, session['user_id']))
        conn.commit()
        conn.close()
        flash('Settings updated successfully!' if new_lang == 'en' else 'Definições atualizadas com sucesso!')
        return redirect(url_for('main.settings'))

    cursor.execute('SELECT avatar, is_private FROM users WHERE id = ?', (session['user_id'],))
    user = cursor.fetchone()
    conn.close()
    is_private_val = user['is_private'] if user and 'is_private' in user.keys() and user['is_private'] is not None else 0
    return render_template('settings.html', current_avatar=user['avatar'] if user else 'ProfileImage#1.png', is_private=is_private_val)

@main_bp.route('/update_avatar', methods=['POST'])
def update_avatar():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    avatar_choice = request.form.get('avatar_choice')
    if avatar_choice and avatar_choice.startswith('ProfileImage#') and avatar_choice.endswith('.png'):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET avatar = ? WHERE id = ?', (avatar_choice, session['user_id']))
        conn.commit()
        conn.close()
        session['avatar'] = avatar_choice
    return redirect(url_for('main.settings'))

@main_bp.route('/save_post/<int:post_id>')
def toggle_save_post(post_id):
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM saved_posts WHERE user_id = ? AND post_id = ?', (user_id, post_id))
    if cursor.fetchone():
        cursor.execute('DELETE FROM saved_posts WHERE user_id = ? AND post_id = ?', (user_id, post_id))
    else:
        cursor.execute('INSERT INTO saved_posts (user_id, post_id) VALUES (?, ?)', (user_id, post_id))
    conn.commit()
    conn.close()
    return redirect(request.referrer or url_for('main.feed'))

@main_bp.route('/follow/<int:user_id>')
def follow_user(user_id):
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    follower_id = session['user_id']
    if follower_id != user_id:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM followers WHERE follower_id = ? AND followed_id = ?', (follower_id, user_id))
        if not cursor.fetchone():
            cursor.execute('INSERT INTO followers (follower_id, followed_id) VALUES (?, ?)', (follower_id, user_id))
            conn.commit()
        conn.close()
    return redirect(request.referrer or url_for('main.profile', user_id=user_id))

@main_bp.route('/unfollow/<int:user_id>')
def unfollow_user(user_id):
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    follower_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM followers WHERE follower_id = ? AND followed_id = ?', (follower_id, user_id))
    conn.commit()
    conn.close()
    return redirect(request.referrer or url_for('main.profile', user_id=user_id))

@main_bp.route('/feed')
def feed():
    tag_filter = request.args.get('tag', '').strip()
    conn = get_db_connection()
    cursor = conn.cursor()

    if tag_filter:
        cursor.execute('''
            SELECT posts.id, posts.user_id, users.username, users.avatar, posts.content, posts.timestamp, posts.is_pigeon
            FROM posts JOIN users ON posts.user_id = users.id
            WHERE posts.content LIKE ? ORDER BY posts.id DESC
        ''', (f'%#{tag_filter}%',))
    else:
        cursor.execute('''
            SELECT posts.id, posts.user_id, users.username, users.avatar, posts.content, posts.timestamp, posts.is_pigeon
            FROM posts JOIN users ON posts.user_id = users.id ORDER BY posts.id DESC
        ''')
    posts = cursor.fetchall()

    posts_data = []
    for p in posts:
        cursor.execute('SELECT COUNT(*) as count FROM likes WHERE post_id = ?', (p['id'],))
        likes_count = cursor.fetchone()['count']
        has_liked = 0
        if 'user_id' in session:
            cursor.execute('SELECT 1 FROM likes WHERE user_id = ? AND post_id = ?', (session['user_id'], p['id']))
            has_liked = 1 if cursor.fetchone() else 0

        cursor.execute('''
            SELECT comments.id, comments.content, comments.timestamp, users.username, users.id as user_id
            FROM comments JOIN users ON comments.user_id = users.id WHERE comments.post_id = ? ORDER BY comments.id ASC
        ''', (p['id'],))
        comments = cursor.fetchall()

        posts_data.append({
            'id': p['id'], 'user_id': p['user_id'], 'username': p['username'], 'avatar': p['avatar'],
            'content': p['content'], 'timestamp': p['timestamp'], 'is_pigeon': p['is_pigeon'],
            'likes_count': likes_count, 'has_liked': has_liked, 'comments': comments
        })
    conn.close()
    return render_template('feed.html', posts=posts_data, active_tag=tag_filter)

@main_bp.route('/post', methods=['POST'])
def create_post():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    content = request.form.get('content', '').strip()
    is_pigeon = 1 if request.form.get('is_pigeon') else 0

    if content:
        now = datetime.now()
        timestamp = now.strftime('%d/%m/%Y às %H:%M')
        today_str = now.strftime('%Y-%m-%d')

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT streak, last_post_date FROM users WHERE id = ?', (session['user_id'],))
        u_data = cursor.fetchone()
        streak = u_data['streak'] or 0
        last_date = u_data['last_post_date']

        if last_date != today_str:
            if last_date:
                l_dt = datetime.strptime(last_date, '%Y-%m-%d')
                diff_days = (now.date() - l_dt.date()).days
                if diff_days == 1:
                    streak += 1
                elif diff_days > 3:
                    streak = 1
            else:
                streak = 1
            cursor.execute('UPDATE users SET streak = ?, last_post_date = ? WHERE id = ?', (streak, today_str, session['user_id']))

        cursor.execute(
            'INSERT INTO posts (user_id, content, timestamp, is_pigeon) VALUES (?, ?, ?, ?)',
            (session['user_id'], content, timestamp, is_pigeon)
        )
        conn.commit()
        conn.close()
        flash('Published successfully!' if session['lang']=='en' else 'Publicado com sucesso!')
    return redirect(url_for('main.feed'))

@main_bp.route('/like/<int:post_id>')
def like_post(post_id):
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM likes WHERE user_id = ? AND post_id = ?', (user_id, post_id))
    if cursor.fetchone():
        cursor.execute('DELETE FROM likes WHERE user_id = ? AND post_id = ?', (user_id, post_id))
    else:
        cursor.execute('INSERT INTO likes (user_id, post_id) VALUES (?, ?)', (user_id, post_id))
    conn.commit()
    conn.close()
    return redirect(request.referrer or url_for('main.feed'))

@main_bp.route('/comment/<int:post_id>', methods=['POST'])
def add_comment(post_id):
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    content = request.form.get('content', '').strip()
    if content:
        timestamp = datetime.now().strftime('%d/%m/%Y às %H:%M')
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO comments (post_id, user_id, content, timestamp) VALUES (?, ?, ?, ?)',
            (post_id, session['user_id'], content, timestamp)
        )
        conn.commit()
        conn.close()
    return redirect(request.referrer or url_for('main.feed'))

@main_bp.route('/profile/<int:user_id>')
def profile(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, avatar, bio, streak, last_post_date, is_perm_banned, banned_until FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        flash('User not found.')
        return redirect(url_for('main.feed'))

    cursor.execute('SELECT COUNT(*) as total FROM posts WHERE user_id = ?', (user_id,))
    total_posts = cursor.fetchone()['total']

    cursor.execute('SELECT COUNT(*) as count FROM followers WHERE followed_id = ?', (user_id,))
    followers_count = cursor.fetchone()['count']

    cursor.execute('SELECT COUNT(*) as count FROM followers WHERE follower_id = ?', (user_id,))
    following_count = cursor.fetchone()['count']

    is_following = 0
    if 'user_id' in session and session['user_id'] != user_id:
        cursor.execute('SELECT 1 FROM followers WHERE follower_id = ? AND followed_id = ?', (session['user_id'], user_id))
        is_following = 1 if cursor.fetchone() else 0

    streak_image = 'FrozenImage.png'
    if user['last_post_date']:
        l_dt = datetime.strptime(user['last_post_date'], '%Y-%m-%d')
        if (datetime.now().date() - l_dt.date()).days <= 1:
            streak_image = 'FireImage.png'

    cursor.execute('SELECT id, content, timestamp, is_pigeon FROM posts WHERE user_id = ? ORDER BY id DESC', (user_id,))
    posts = cursor.fetchall()

    saved_posts = []
    if 'user_id' in session and session['user_id'] == user_id:
        cursor.execute('''
            SELECT posts.id, posts.user_id, users.username, users.avatar, posts.content, posts.timestamp, posts.is_pigeon
            FROM saved_posts JOIN posts ON saved_posts.post_id = posts.id
            JOIN users ON posts.user_id = users.id WHERE saved_posts.user_id = ? ORDER BY saved_posts.id DESC
        ''', (user_id,))
        saved_posts = cursor.fetchall()

    conn.close()

    return render_template('profile.html', profile_user=user, posts=posts, saved_posts=saved_posts, total_posts=total_posts,
                           followers_count=followers_count, following_count=following_count,
                           is_following=is_following, streak_image=streak_image)

@main_bp.route('/update_bio', methods=['POST'])
def update_bio():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    bio = request.form.get('bio', '').strip()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET bio = ? WHERE id = ?', (bio, session['user_id']))
    conn.commit()
    conn.close()
    return redirect(url_for('main.profile', user_id=session['user_id']))

@main_bp.route('/chat/<int:user_id>', methods=['GET', 'POST'])
def chat(user_id):
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    current_user_id = session['user_id']
    if current_user_id == user_id:
        return redirect(url_for('main.feed'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, avatar FROM users WHERE id = ?', (user_id,))
    target_user = cursor.fetchone()
    if not target_user:
        conn.close()
        return redirect(url_for('main.feed'))
    if request.method == 'POST':
        msg_content = request.form.get('content', '').strip()
        if msg_content:
            timestamp = datetime.now().strftime('%d/%m/%Y às %H:%M')
            cursor.execute('INSERT INTO messages (sender_id, receiver_id, content, timestamp) VALUES (?, ?, ?, ?)', (current_user_id, user_id, msg_content, timestamp))
            conn.commit()
        conn.close()
        return redirect(url_for('main.chat', user_id=user_id))
    cursor.execute('SELECT * FROM messages WHERE (sender_id = ? AND receiver_id = ?) OR (sender_id = ? AND receiver_id = ?) ORDER BY id ASC', (current_user_id, user_id, user_id, current_user_id))
    messages = cursor.fetchall()
    conn.close()
    return render_template('chat.html', target_user=target_user, messages=messages)

@main_bp.route('/banned')
def banned():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT is_perm_banned, banned_until, appeal_msg FROM users WHERE id = ?', (session['user_id'],))
    user = cursor.fetchone()
    conn.close()
    return render_template('banned.html', user=user)

@main_bp.route('/submit_appeal', methods=['POST'])
def submit_appeal():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    appeal_text = request.form.get('appeal_text', '').strip()
    if appeal_text:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET appeal_msg = ? WHERE id = ?', (appeal_text, session['user_id']))
        conn.commit()
        conn.close()
    return redirect(url_for('main.banned'))

@main_bp.route('/admin/action/<int:user_id>/<action>', methods=['POST'])
def admin_action(user_id, action):
    if session.get('user_id') != 1:
        return redirect(url_for('main.feed'))
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now()
    if action == 'ban_custom':
        days = int(request.form.get('days', 1))
        b_until = (now + timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('UPDATE users SET banned_until = ? WHERE id = ?', (b_until, user_id))
    elif action == 'unban_temp':
        cursor.execute('UPDATE users SET banned_until = NULL WHERE id = ?', (user_id,))
    elif action == 'ban_perm':
        p_date = now.strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('UPDATE users SET is_perm_banned = 1, perm_banned_date = ?, username = ? WHERE id = ?', (p_date, f"Banned#{user_id}", user_id))
    elif action == 'unban_perm':
        cursor.execute('UPDATE users SET is_perm_banned = 0, perm_banned_date = NULL WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('main.profile', user_id=user_id))

# --- Rotas de Jogos e Ranking ---
@main_bp.route('/games')
def games():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT username, avatar, playtime FROM users WHERE playtime > 0 ORDER BY playtime DESC LIMIT 10')
    top_players = cursor.fetchall()
    conn.close()
    return render_template('games.html', top_players=top_players)

@main_bp.route('/games/subway-surfers')
def subway_surfers():
    return render_template('subway_surfers.html')

@main_bp.route('/games/temple-run')
def temple_run():
    return render_template('temple_run.html')

@main_bp.route('/games/fruit-ninja')
def fruit_ninja():
    return render_template('fruit_ninja.html')

@main_bp.route('/update_playtime', methods=['POST'])
def update_playtime():
    if 'user_id' not in session:
        return {'status': 'unauthorized'}, 401

    try:
        seconds = int(request.form.get('seconds', 10))
    except ValueError:
        seconds = 10

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET playtime = playtime + ? WHERE id = ?', (seconds, session['user_id']))
        conn.commit()
    except Exception as e:
        conn.rollback()
        return {'status': 'error', 'message': str(e)}, 500
    finally:
        conn.close()

    return {'status': 'success'}
